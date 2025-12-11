from fastapi import Depends

from src.core.config import DB_PATH
from src.data.repositories.sqlite_repo import (
    SQLiteConnectionManager,
    SQLiteUserRepository,
    SQLiteVideoRepository,
    SQLiteHistoryRepository,
)
from src.services.auth_service import AuthService
from src.services.video_service import VideoService
from src.services.history_service import HistoryService

# Single connection manager (creates connections on demand)
_connection_manager = SQLiteConnectionManager(DB_PATH)


def get_user_repo():
    conn = _connection_manager()
    return SQLiteUserRepository(conn)


def get_video_repo():
    conn = _connection_manager()
    return SQLiteVideoRepository(conn)


def get_history_repo():
    conn = _connection_manager()
    return SQLiteHistoryRepository(conn)


def get_auth_service(user_repo=Depends(get_user_repo)) -> AuthService:
    return AuthService(user_repo=user_repo)


def get_video_service(video_repo=Depends(get_video_repo)) -> VideoService:
    return VideoService(video_repo=video_repo)


def get_history_service(history_repo=Depends(get_history_repo)) -> HistoryService:
    return HistoryService(history_repo=history_repo)
