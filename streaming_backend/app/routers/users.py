from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user_from_request
from app.db.session import get_db
from app.schemas.history import HistoryItem, HistoryListResponse, ProgressUpdateRequest
from app.services.history_service import HistoryService
from app.schemas.video import VideoOut

router = APIRouter(prefix="/users", tags=["users"])


def _video_to_out(request: Request, video) -> VideoOut:
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
    "/history",
    response_model=HistoryListResponse,
    summary="Get watch history",
    description="Returns watch history entries (video + progress) for the authenticated user.",
)
def get_history(request: Request, db: Session = Depends(get_db)) -> HistoryListResponse:
    user = get_current_user_from_request(request, db)
    service = HistoryService(db)
    entries = service.list_for_user(user["id"])

    items: list[HistoryItem] = []
    for e in entries:
        # joinedload ensures e.video exists
        items.append(
            HistoryItem(video=_video_to_out(request, e.video), progress_seconds=int(e.progress_seconds))
        )

    return HistoryListResponse(items=items)


@router.put(
    "/history/{video_id}",
    response_model=HistoryItem,
    summary="Update watch progress",
    description=(
        "Upserts the watch progress for a video for the authenticated user. "
        "Call periodically from the player (e.g., every few seconds)."
    ),
)
def update_history(
    video_id: int,
    payload: ProgressUpdateRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> HistoryItem:
    user = get_current_user_from_request(request, db)
    service = HistoryService(db)
    try:
        entry = service.update_progress(
            user_id=user["id"], video_id=video_id, progress_seconds=payload.progress_seconds
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

    return HistoryItem(video=_video_to_out(request, entry.video), progress_seconds=int(entry.progress_seconds))
