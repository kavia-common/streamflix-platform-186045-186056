from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.video import Video
from app.repositories.video_repository import VideoRepository


class VideoService:
    """Business logic for video listing and search."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._videos = VideoRepository(db)

    def get(self, video_id: int) -> Video | None:
        return self._videos.get(video_id)

    def search(self, q: str | None, tag: str | None, limit: int, offset: int) -> tuple[list[Video], int]:
        limit = max(1, min(limit, 100))
        offset = max(0, offset)
        return self._videos.search(q=q, tag=tag, limit=limit, offset=offset)
