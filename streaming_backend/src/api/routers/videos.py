import mimetypes
import os
from typing import List, Any

from fastapi import APIRouter, Depends, HTTPException, Request

from src.core.config import MEDIA_DIR
from src.core.di import get_video_service
from src.core.range_stream import range_stream_response
from src.domain.models import VideoOut
from src.services.video_service import VideoService

router = APIRouter(prefix="/videos", tags=["Videos"])


@router.get("", summary="List Videos", description="List all available videos.", response_model=List[VideoOut])
def list_videos(video_service: VideoService = Depends(get_video_service)) -> Any:
    """Return video metadata list."""
    videos = video_service.list_videos()
    return videos


@router.get("/{video_id}", summary="Get Video", description="Get video metadata by ID.", response_model=VideoOut)
def get_video(video_id: int, video_service: VideoService = Depends(get_video_service)) -> Any:
    """Return a specific video's metadata."""
    v = video_service.get_video(video_id)
    return v


@router.get("/stream/{video_id}", summary="Stream Video", description="Stream video content with HTTP Range support.")
def stream_video(video_id: int, request: Request, video_service: VideoService = Depends(get_video_service)):
    """Stream the video bytes using HTTP Range."""
    v = video_service.get_video(video_id)
    file_path = os.path.join(MEDIA_DIR, v["filename"])
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Media file not found")

    range_header = request.headers.get("range")
    content_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
    return range_stream_response(file_path=file_path, filename=v["filename"], range_header=range_header, content_type=content_type)
