from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.watch_history import WatchHistory
from app.repositories.history_repository import HistoryRepository
from app.repositories.video_repository import VideoRepository


class HistoryService:
    """Business logic for user watch history."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._history = HistoryRepository(db)
        self._videos = VideoRepository(db)

    def list_for_user(self, user_id: int) -> list[WatchHistory]:
        return self._history.list_for_user(user_id)

    def update_progress(self, user_id: int, video_id: int, progress_seconds: int) -> WatchHistory:
        video = self._videos.get(video_id)
        if not video:
            raise ValueError("Video not found")

        entry = self._history.upsert_progress(
            user_id=user_id, video_id=video_id, progress_seconds=progress_seconds
        )
        self._db.commit()
        self._db.refresh(entry)
        return entry
