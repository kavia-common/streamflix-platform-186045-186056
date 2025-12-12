from __future__ import annotations

from pydantic import Field

from app.schemas.common import APIModel


class VideoOut(APIModel):
    id: int = Field(..., description="Video id")
    title: str = Field(..., description="Video title")
    description: str = Field(..., description="Video description")
    tags: str = Field(..., description="Comma-separated tags")
    duration_seconds: int | None = Field(None, description="Duration in seconds (optional)")
    content_type: str = Field(..., description="MIME content type")
    stream_url: str = Field(..., description="Streaming URL for HTTP Range playback")


class VideoListResponse(APIModel):
    items: list[VideoOut] = Field(..., description="Videos")
    total: int = Field(..., description="Total videos matching query")
    limit: int = Field(..., description="Page size")
    offset: int = Field(..., description="Offset")
