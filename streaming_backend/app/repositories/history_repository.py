from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.watch_history import WatchHistory


class HistoryRepository:
    """Data access for watch history."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def list_for_user(self, user_id: int) -> list[WatchHistory]:
        stmt = (
            select(WatchHistory)
            .options(joinedload(WatchHistory.video))
            .where(WatchHistory.user_id == user_id)
            .order_by(WatchHistory.updated_at.desc())
        )
        return list(self._db.scalars(stmt).all())

    def get_for_user_and_video(self, user_id: int, video_id: int) -> WatchHistory | None:
        stmt = select(WatchHistory).where(
            WatchHistory.user_id == user_id, WatchHistory.video_id == video_id
        )
        return self._db.scalar(stmt)

    def upsert_progress(self, user_id: int, video_id: int, progress_seconds: int) -> WatchHistory:
        entry = self.get_for_user_and_video(user_id=user_id, video_id=video_id)
        if entry is None:
            entry = WatchHistory(user_id=user_id, video_id=video_id, progress_seconds=progress_seconds)
            self._db.add(entry)
        else:
            entry.progress_seconds = progress_seconds

        self._db.flush()
        return entry
