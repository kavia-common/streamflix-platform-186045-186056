from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.video import VideoListResponse, VideoOut
from app.services.video_service import VideoService
from app.services.streaming_service import build_file_range, iter_file_bytes
from app.core.config import get_settings

router = APIRouter(prefix="/videos", tags=["videos"])


def _to_video_out(request: Request, video) -> VideoOut:
    stream_url = str(request.url_for("stream_video", id=video.id))
    return VideoOut(
        id=video.id,
        title=video.title,
        description=video.description,
        tags=video.tags,
        duration_seconds=video.duration_seconds,
        content_type=video.content_type,
        stream_url=stream_url,
    )


@router.get(
    "",
    response_model=VideoListResponse,
    summary="List/search videos",
    description="Lists videos with optional text search (q) and tag filtering.",
)
def list_videos(
    request: Request,
    q: str | None = None,
    tag: str | None = None,
    limit: int = 24,
    offset: int = 0,
    db: Session = Depends(get_db),
) -> VideoListResponse:
    service = VideoService(db)
    items, total = service.search(q=q, tag=tag, limit=limit, offset=offset)
    return VideoListResponse(
        items=[_to_video_out(request, v) for v in items],
        total=total,
        limit=max(1, min(limit, 100)),
        offset=max(0, offset),
    )


@router.get(
    "/{id}",
    response_model=VideoOut,
    summary="Get video detail",
    description="Returns metadata for a single video.",
)
def get_video(id: int, request: Request, db: Session = Depends(get_db)) -> VideoOut:
    service = VideoService(db)
    video = service.get(id)
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    return _to_video_out(request, video)


@router.get(
    "/{id}/stream",
    name="stream_video",
    summary="Stream video (HTTP Range)",
    description=(
        "Streams the video file with HTTP Range support for HTML5 playback. "
        "Clients should send a `Range: bytes=start-end` header for seeking."
    ),
)
def stream_video(id: int, request: Request, response: Response, db: Session = Depends(get_db)):
    service = VideoService(db)
    video = service.get(id)
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")

    range_header = request.headers.get("range")
    file_range = build_file_range(
        file_path=video.file_path, content_type_fallback=video.content_type, range_header=range_header
    )

    # Resolve the final path similarly to the build_file_range logic
    settings = get_settings()
    from pathlib import Path  # local import to keep module load light

    base = Path(settings.video_library_path)
    path = Path(video.file_path)
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()
    if not path.exists():
        candidate = (base / video.file_path).resolve()
        if candidate.exists():
            path = candidate

    content_length = file_range.end - file_range.start + 1
    headers = {
        "Accept-Ranges": "bytes",
        "Content-Type": file_range.content_type,
    }

    if range_header:
        # Partial content
        headers["Content-Range"] = f"bytes {file_range.start}-{file_range.end}/{file_range.size}"
        headers["Content-Length"] = str(content_length)
        response.status_code = status.HTTP_206_PARTIAL_CONTENT
    else:
        headers["Content-Length"] = str(file_range.size)
        response.status_code = status.HTTP_200_OK

    for k, v in headers.items():
        response.headers[k] = v

    from fastapi.responses import StreamingResponse

    return StreamingResponse(
        iter_file_bytes(path=path, start=file_range.start, end=file_range.end),
        status_code=response.status_code,
        media_type=file_range.content_type,
        headers=headers,
    )
