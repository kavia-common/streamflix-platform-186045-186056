from typing import List, Dict, Any

from src.data.repositories.base import HistoryRepository


class HistoryService:
    """Business logic for watch history."""

    def __init__(self, history_repo: HistoryRepository):
        self.history_repo = history_repo

    # PUBLIC_INTERFACE
    def upsert(self, user_id: int, video_id: int, position_seconds: int) -> Dict[str, Any]:
        """Create or update a history entry for a user and video."""
        return self.history_repo.upsert_history(user_id=user_id, video_id=video_id, position_seconds=position_seconds)

    # PUBLIC_INTERFACE
    def list_for_user(self, user_id: int) -> List[Dict[str, Any]]:
        """List history entries for a user."""
        return self.history_repo.list_history_for_user(user_id=user_id)
