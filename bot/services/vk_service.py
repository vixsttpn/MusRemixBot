"""VK API service for audio search and download"""
import logging
import asyncio
from typing import List, Optional
import aiohttp
from ..config import VK_TOKEN, VK_VERSION, SEARCH_TIMEOUT
from ..models import Track

logger = logging.getLogger(__name__)


class VKService:
    """Сервис для работы с VK"""
    
    BASE_URL = "https://api.vk.com/method"
    
    def __init__(self):
        self.token = VK_TOKEN
        self.version = VK_VERSION
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def init_session(self):
        """Инициализировать сессию"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def close_session(self):
        """Закрыть сессию"""
        if self.session:
            await self.session.close()
    
    async def search_audio(
        self,
        query: str,
        limit: int = 50
    ) -> List[Track]:
        """
        Поиск аудио в VK
        
        Args:
            query: поисковый запрос
            limit: максимум результатов
        
        Returns:
            Список найденных треков
        """
        if not self.token:
            logger.warning("VK_TOKEN not configured")
            return []
        
        await self.init_session()
        
        params = {
            'access_token': self.token,
            'v': self.version,
            'method': 'audio.search',
            'q': query,
            'count': min(limit, 300),
            'auto_complete': 1,
            'sort': 2,  # по популярности
        }
        
        try:
            async with asyncio.timeout(SEARCH_TIMEOUT):
                async with self.session.get(
                    f"{self.BASE_URL}/audio.search",
                    params=params
                ) as resp:
                    if resp.status != 200:
                        logger.error(f"VK API error: {resp.status}")
                        return []
                    
                    data = await resp.json()
                    
                    # Обработка ошибок VK
                    if 'error' in data:
                        logger.error(f"VK error: {data['error']}")
                        return []
                    
                    items = data.get('response', {}).get('items', [])
                    
                    tracks = []
                    for item in items:
                        track = self._parse_audio_item(item)
                        if track:
                            tracks.append(track)
                    
                    logger.info(f"Found {len(tracks)} tracks in VK")
                    return tracks
        
        except asyncio.TimeoutError:
            logger.error("VK search timeout")
            return []
        except Exception as e:
            logger.error(f"VK search error: {e}")
            return []
    
    async def get_audio_url(self, audio_id: str) -> Optional[str]:
        """
        Получить прямую ссылку на аудиофайл
        
        Args:
            audio_id: ID аудиозаписи в формате owner_id_audio_id
        
        Returns:
            URL аудиофайла или None
        """
        if not self.token:
            return None
        
        await self.init_session()
        
        params = {
            'access_token': self.token,
            'v': self.version,
            'method': 'audio.getById',
            'audios': audio_id,
        }
        
        try:
            async with asyncio.timeout(10):
                async with self.session.get(
                    f"{self.BASE_URL}/audio.getById",
                    params=params
                ) as resp:
                    data = await resp.json()
                    
                    if 'error' in data:
                        logger.warning(f"Cannot get audio URL: {data['error']}")
                        return None
                    
                    items = data.get('response', [])
                    if items and 'url' in items[0]:
                        return items[0]['url']
                    
                    return None
        
        except Exception as e:
            logger.error(f"Error getting audio URL: {e}")
            return None
    
    async def download_audio(
        self,
        url: str,
        output_path: str,
        timeout: int = 30
    ) -> bool:
        """
        Скачать аудиофайл
        
        Args:
            url: URL аудиофайла
            output_path: путь для сохранения
            timeout: таймаут в секундах
        
        Returns:
            True если успешно
        """
        await self.init_session()
        
        try:
            async with asyncio.timeout(timeout):
                async with self.session.get(url) as resp:
                    if resp.status != 200:
                        logger.error(f"Download error: {resp.status}")
                        return False
                    
                    with open(output_path, 'wb') as f:
                        async for chunk in resp.content.iter_chunked(8192):
                            f.write(chunk)
                    
                    logger.info(f"Downloaded to {output_path}")
                    return True
        
        except asyncio.TimeoutError:
            logger.error("Download timeout")
            return False
        except Exception as e:
            logger.error(f"Download error: {e}")
            return False
    
    @staticmethod
    def _parse_audio_item(item: dict) -> Optional[Track]:
        """Парсить элемент аудио из VK API"""
        try:
            return Track(
                id=f"{item['owner_id']}_{item['id']}",
                title=item.get('title', 'Unknown'),
                artist=item.get('artist', 'Unknown'),
                duration=item.get('duration', 0),
                url=item.get('url', ''),
                source='vk'
            )
        except (KeyError, ValueError):
            return None
