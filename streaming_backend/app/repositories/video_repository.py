from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.video import Video


class VideoRepository:
    """Data access for videos."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get(self, video_id: int) -> Video | None:
        return self._db.get(Video, video_id)

    def search(self, q: str | None, tag: str | None, limit: int, offset: int) -> tuple[list[Video], int]:
        stmt = select(Video)
        count_stmt = select(func.count()).select_from(Video)

        if q:
            like = f"%{q}%"
            stmt = stmt.where((Video.title.ilike(like)) | (Video.description.ilike(like)))
            count_stmt = count_stmt.where((Video.title.ilike(like)) | (Video.description.ilike(like)))

        if tag:
            # Simple comma-separated tag search.
            like = f"%{tag}%"
            stmt = stmt.where(Video.tags.ilike(like))
            count_stmt = count_stmt.where(Video.tags.ilike(like))

        total = int(self._db.scalar(count_stmt) or 0)
        items = list(self._db.scalars(stmt.order_by(Video.id.desc()).limit(limit).offset(offset)).all())
        return items, total
