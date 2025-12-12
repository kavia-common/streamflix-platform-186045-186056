from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.db.init_db import init_db
from app.routers import auth, users, videos

openapi_tags = [
    {"name": "auth", "description": "JWT cookie-based authentication"},
    {"name": "videos", "description": "Video metadata, search, and streaming"},
    {"name": "users", "description": "User-specific endpoints (watch history)"},
]

app = FastAPI(
    title="StreamFlix Backend API",
    description=(
        "Backend API for StreamFlix: authentication, video discovery, watch history, "
        "and HTTP Range streaming suitable for HTML5 video players."
    ),
    version="0.1.0",
    openapi_tags=openapi_tags,
)


@app.on_event("startup")
def _startup() -> None:
    init_db()


def _configure_cors() -> None:
    settings = get_settings()
    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,  # required for cookie auth
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["Content-Range", "Accept-Ranges", "Content-Length"],
        )


_configure_cors()

app.include_router(auth.router)
app.include_router(videos.router)
app.include_router(users.router)
