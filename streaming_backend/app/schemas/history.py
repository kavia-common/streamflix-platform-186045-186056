from __future__ import annotations

from pydantic import Field

from app.schemas.common import APIModel
from app.schemas.video import VideoOut


class HistoryItem(APIModel):
    video: VideoOut = Field(..., description="Video metadata")
    progress_seconds: int = Field(..., ge=0, description="Last watched position in seconds")


class HistoryListResponse(APIModel):
    items: list[HistoryItem] = Field(..., description="History entries for the current user")


class ProgressUpdateRequest(APIModel):
    progress_seconds: int = Field(..., ge=0, description="New playback position in seconds")
