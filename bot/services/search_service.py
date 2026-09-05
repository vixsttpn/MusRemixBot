"""Search service with normalization and fuzzy matching"""
import re
import logging
from typing import List, Optional, Tuple
from difflib import SequenceMatcher, get_close_matches
from ..models import Track, SearchResult

logger = logging.getLogger(__name__)


class SearchNormalizer:
    """Нормализация поисковых запросов"""
    
    # Русский + английский alphabet
    TRANSLITERATION_MAP = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
        'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i',
        'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
        'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
        'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch',
        'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '',
        'э': 'e', 'ю': 'yu', 'я': 'ya'
    }
    
    COMMON_TYPOS = {
        'нагйкоре': 'nightcore',
        'ночнкоре': 'nightcore',
        'слоуд': 'slowed',
        'сларед': 'slowed',
        'спиду': 'speed',
        'басс': 'bass',
        'ремикс': 'remix',
    }
    
    STOP_WORDS = {
        'найди', 'поиск', 'ищи', 'включи', 'включить',
        'сыграй', 'play', 'find', 'search', 'put on',
        'мне', 'мне пожалуйста', 'пожалуйста', 'please',
        'песню', 'песня', 'трек', 'музыку', 'song', 'track',
    }
    
    @staticmethod
    def normalize(query: str) -> Tuple[str, Optional[str]]:
        """
        Нормализовать запрос
        
        Returns:
            (normalized_query, suggested_correction)
        """
        if not query or not query.strip():
            return "", None
        
        # Приведение к нижнему регистру
        normalized = query.lower().strip()
        
        # Удаление лишних пробелов
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Удаление пунктуации в начале/конце
        normalized = re.sub(r'^[^а-яa-z0-9]+|[^а-яa-z0-9]+$', '', normalized)
        
        # Удаление stop words
        for word in SearchNormalizer.STOP_WORDS:
            normalized = re.sub(rf'\b{word}\b', '', normalized, flags=re.IGNORECASE)
        
        # Очистка пробелов снова
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        # Замена очевидных опечаток
        suggestion = None
        for typo, correction in SearchNormalizer.COMMON_TYPOS.items():
            if typo in normalized:
                normalized = normalized.replace(typo, correction)
                suggestion = correction
        
        return normalized, suggestion
    
    @staticmethod
    def transliterate(text: str) -> str:
        """Транслитерация"""
        result = []
        for char in text.lower():
            result.append(
                SearchNormalizer.TRANSLITERATION_MAP.get(char, char)
            )
        return ''.join(result)
    
    @staticmethod
    def similarity(a: str, b: str) -> float:
        """Рассчитать схожесть двух строк (0-1)"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()


class SearchService:
    """Сервис поиска"""
    
    def __init__(self, vk_service):
        self.vk_service = vk_service
        self.normalizer = SearchNormalizer()
    
    async def search(
        self,
        query: str,
        limit: int = 50,
        include_variants: bool = True
    ) -> SearchResult:
        """
        Поиск музыки
        
        Args:
            query: поисковый запрос
            limit: максимум результатов
            include_variants: включать ли варианты (слоуд, спид и т.д.)
        
        Returns:
            SearchResult с найденными треками
        """
        normalized_query, suggestion = self.normalizer.normalize(query)
        
        if not normalized_query:
            logger.warning(f"Empty query after normalization: {query}")
            return SearchResult(query, [], 0, suggestion)
        
        logger.info(f"Searching for: {normalized_query}")
        
        # Основной поиск в VK
        tracks = await self.vk_service.search_audio(normalized_query, limit)
        
        # Дополнительный поиск вариантов если требуется
        if include_variants and len(tracks) > 0:
            tracks = self._add_variants(tracks)
        
        # Дедупликация
        tracks = self._deduplicate(tracks)
        
        # Сортировка по релевантности
        tracks = self._rank_by_relevance(tracks, normalized_query)
        
        return SearchResult(
            query=normalized_query,
            tracks=tracks[:limit],
            total_found=len(tracks),
            query_corrected=suggestion
        )
    
    def _add_variants(self, tracks: List[Track]) -> List[Track]:
        """Добавить варианты обработки (slowed, sped up и т.д.)"""
        # Для каждого трека попытаться найти варианты
        variants = []
        for track in tracks:
            variants.append(track)
            
            # Поиск вариантов через добавление ключевых слов
            for variant in ['slowed', 'sped up', 'bass boosted', 'nightcore', 'reverb']:
                search_key = f"{track.title} {variant}"
                # Это просто маркер, реальный поиск будет в handlers
                pass
        
        return variants
    
    def _deduplicate(self, tracks: List[Track]) -> List[Track]:
        """Удалить дубликаты"""
        seen = {}
        unique = []
        
        for track in tracks:
            key = f"{track.artist.lower()}_{track.title.lower()}"
            if key not in seen:
                seen[key] = True
                unique.append(track)
        
        return unique
    
    def _rank_by_relevance(
        self,
        tracks: List[Track],
        query: str
    ) -> List[Track]:
        """Отранжировать по релевантности"""
        def relevance_score(track: Track) -> float:
            score = 0.0
            
            # Точное совпадение названия
            if query.lower() == track.title.lower():
                score += 100
            
            # Точное совпадение исполнителя
            if query.lower() == track.artist.lower():
                score += 80
            
            # Начинается с запроса
            if track.title.lower().startswith(query.lower()):
                score += 50
            if track.artist.lower().startswith(query.lower()):
                score += 40
            
            # Содержит запрос
            if query.lower() in track.title.lower():
                score += 30
            if query.lower() in track.artist.lower():
                score += 20
            
            # Схожесть
            title_sim = self.normalizer.similarity(query, track.title)
            artist_sim = self.normalizer.similarity(query, track.artist)
            score += (title_sim * 25) + (artist_sim * 15)
            
            return score
        
        return sorted(tracks, key=relevance_score, reverse=True)
    
    async def fuzzy_search(
        self,
        query: str,
        previous_results: List[Track],
        threshold: float = 0.6
    ) -> Optional[List[Track]]:
        """
        Fuzzy поиск при плохом распознавании voice
        
        Args:
            query: распознанный текст (может быть с ошибками)
            previous_results: предыдущие результаты для уточнения
            threshold: порог схожести
        
        Returns:
            Уточнённые результаты или None
        """
        if not previous_results:
            return None
        
        # Получить близкие совпадения
        close_matches = get_close_matches(
            query.lower(),
            [f"{t.artist} {t.title}".lower() for t in previous_results],
            n=5,
            cutoff=threshold
        )
        
        if close_matches:
            return [t for t in previous_results 
                   if f"{t.artist} {t.title}".lower() in close_matches]
        
        return None
