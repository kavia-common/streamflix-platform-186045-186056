from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

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

# If running behind a reverse proxy (common in preview deployments), trust forwarded headers
# so `request.url_for()` generates correct https:// URLs and hostnames.
if os.getenv("TRUST_PROXY", "false").lower() in {"1", "true", "yes", "on"}:
    app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

app.include_router(auth.router)
app.include_router(videos.router)
app.include_router(users.router)
