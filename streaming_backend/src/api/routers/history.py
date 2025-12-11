from typing import List, Any

from fastapi import APIRouter, Depends

from src.core.dependencies import get_current_user
from src.core.di import get_history_service
from src.domain.models import HistoryCreate, HistoryOut
from src.services.history_service import HistoryService

router = APIRouter(prefix="/users/history", tags=["History"])


@router.get("", summary="Get Watch History", description="Get the authenticated user's watch history.", response_model=List[HistoryOut])
def get_history(user=Depends(get_current_user), history_service: HistoryService = Depends(get_history_service)) -> Any:
    """List the watch history for the current user."""
    items = history_service.list_for_user(user_id=user["id"])
    return items


@router.post("", summary="Upsert Watch History", description="Create or update a history entry for the authenticated user.", response_model=HistoryOut)
def upsert_history(payload: HistoryCreate, user=Depends(get_current_user), history_service: HistoryService = Depends(get_history_service)) -> Any:
    """Upsert a watch history record for the current user."""
    item = history_service.upsert(user_id=user["id"], video_id=payload.video_id, position_seconds=payload.position_seconds)
    return item
