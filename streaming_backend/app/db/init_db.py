from __future__ import annotations

import mimetypes
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import engine
from app.models.video import Video
from app.models.watch_history import WatchHistory
from app.models.user import User  # noqa: F401  # imported for side-effect (table registration)
from app.db.base import Base


# PUBLIC_INTERFACE
def init_db() -> None:
    """Create database tables and run idempotent seed logic."""
    Base.metadata.create_all(bind=engine)

    # Seed videos from the configured library path (idempotent).
    settings = get_settings()
    library = Path(settings.video_library_path)
    if not library.exists() or not library.is_dir():
        return

    with Session(engine) as db:
        _seed_videos_from_library(db, library)
        db.commit()


def _seed_videos_from_library(db: Session, library: Path) -> None:
    # Recognize typical video extensions.
    exts = {".mp4", ".webm", ".mov", ".mkv", ".m4v"}
    for path in sorted(library.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in exts:
            continue

        # Use relative path if possible to keep deployments portable.
        try:
            file_path = str(path.relative_to(Path.cwd()))
        except ValueError:
            file_path = str(path)

        existing = db.scalar(select(Video).where(Video.file_path == file_path))
        if existing:
            continue

        mime, _ = mimetypes.guess_type(str(path))
        db.add(
            Video(
                title=path.stem.replace("_", " ").replace("-", " "),
                description="",
                file_path=file_path,
                content_type=mime or "video/mp4",
                duration_seconds=None,
                tags="",
            )
        )
