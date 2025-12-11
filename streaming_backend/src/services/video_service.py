from typing import List, Dict, Any

from fastapi import HTTPException, status

from src.data.repositories.base import VideoRepository


class VideoService:
    """Business logic for videos."""

    def __init__(self, video_repo: VideoRepository):
        self.video_repo = video_repo

    # PUBLIC_INTERFACE
    def list_videos(self) -> List[Dict[str, Any]]:
        """List all videos with metadata."""
        return self.video_repo.list_videos()

    # PUBLIC_INTERFACE
    def get_video(self, video_id: int) -> Dict[str, Any]:
        """Get a single video by ID or 404."""
        v = self.video_repo.get_video(video_id)
        if not v:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
        return v
