from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Video(Base):
    """Video metadata and storage reference (file path)."""

    __tablename__ = "videos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    file_path: Mapped[str] = mapped_column(String(500), unique=True, index=True, nullable=False)
    content_type: Mapped[str] = mapped_column(String(120), nullable=False, default="video/mp4")
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tags: Mapped[str] = mapped_column(String(500), nullable=False, default="")  # comma-separated

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    history = relationship("WatchHistory", back_populates="video", cascade="all, delete-orphan")
