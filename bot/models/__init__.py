"""Models module"""
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum


class RemixType(str, Enum):
    """Типы обработки"""
    ORIGINAL = "original"
    SLOWED = "slowed"
    SPED_UP = "sped_up"
    BASS_BOOSTED = "bass_boosted"
    NIGHTCORE = "nightcore"
    REVERB = "reverb"
    LOFI = "lofi"
    ACOUSTIC = "acoustic"
    INSTRUMENTAL = "instrumental"
    LIVE = "live"
    COVER = "cover"
    EDIT = "edit"


@dataclass
class Track:
    """Трек"""
    id: str
    title: str
    artist: str
    duration: int
    url: str
    source: str  # 'vk', 'youtube', etc.
    
    def __str__(self) -> str:
        return f"{self.artist} — {self.title}"


@dataclass
class SearchResult:
    """Результат поиска"""
    query: str
    tracks: List[Track]
    total_found: int
    query_corrected: Optional[str] = None


@dataclass
class UserContext:
    """Контекст пользователя"""
    user_id: int
    current_query: Optional[str] = None
    search_results: Optional[List[Track]] = None
    selected_track: Optional[Track] = None
    selected_remix: Optional[RemixType] = None
    search_page: int = 0
    
    def reset(self):
        """Сбросить контекст"""
        self.current_query = None
        self.search_results = None
        self.selected_track = None
        self.selected_remix = None
        self.search_page = 0
    
    def reset_selection(self):
        """Сбросить только выбор (для новой песни)"""
        self.selected_track = None
        self.selected_remix = None
        self.search_page = 0
