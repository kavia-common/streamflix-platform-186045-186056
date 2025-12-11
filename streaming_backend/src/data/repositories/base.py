from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any


class BaseRepository(ABC):
    """Base repository interface for data access abstraction."""
    pass


class UserRepository(BaseRepository):
    """Abstract user repository."""

    @abstractmethod
    def create_user(self, email: str, password_hash: str) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        raise NotImplementedError


class VideoRepository(BaseRepository):
    """Abstract video repository."""

    @abstractmethod
    def list_videos(self) -> List[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def get_video(self, video_id: int) -> Optional[Dict[str, Any]]:
        raise NotImplementedError


class HistoryRepository(BaseRepository):
    """Abstract watch history repository."""

    @abstractmethod
    def upsert_history(self, user_id: int, video_id: int, position_seconds: int) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def list_history_for_user(self, user_id: int) -> List[Dict[str, Any]]:
        raise NotImplementedError
