from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List


def _parse_csv(value: str | None) -> List[str]:
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment variables.

    Note: We intentionally keep this lightweight (no external settings library) to reduce
    dependencies and keep config behavior explicit and deterministic.
    """

    database_url: str | None
    sqlite_path: str | None

    jwt_secret: str
    jwt_expires_minutes: int
    jwt_cookie_name: str

    cookie_secure: bool
    cookie_domain: str | None
    cookie_samesite: str

    cors_origins: List[str]

    video_library_path: str
    stream_chunk_size: int


# PUBLIC_INTERFACE
def get_settings() -> Settings:
    """Load and return application Settings from environment variables."""
    database_url = os.getenv("DATABASE_URL")
    sqlite_path = os.getenv("SQLITE_PATH")

    jwt_secret = os.getenv("JWT_SECRET", "")
    if not jwt_secret:
        # This must be provided by the orchestrator/user in .env for real deployments.
        raise RuntimeError("JWT_SECRET is required but not set")

    jwt_expires_minutes = int(os.getenv("JWT_EXPIRES_MINUTES", "10080"))
    jwt_cookie_name = os.getenv("JWT_COOKIE_NAME", "streamflix_access")

    cookie_secure = os.getenv("COOKIE_SECURE", "true").lower() in {"1", "true", "yes", "on"}
    cookie_domain = os.getenv("COOKIE_DOMAIN") or None
    cookie_samesite = os.getenv("COOKIE_SAMESITE", "lax").lower()

    # Prefer existing template env var names if present.
    cors_origins = _parse_csv(os.getenv("CORS_ORIGINS")) or _parse_csv(os.getenv("ALLOWED_ORIGINS"))

    video_library_path = os.getenv("VIDEO_LIBRARY_PATH", "media")
    stream_chunk_size = int(os.getenv("STREAM_CHUNK_SIZE", "1048576"))

    return Settings(
        database_url=database_url,
        sqlite_path=sqlite_path,
        jwt_secret=jwt_secret,
        jwt_expires_minutes=jwt_expires_minutes,
        jwt_cookie_name=jwt_cookie_name,
        cookie_secure=cookie_secure,
        cookie_domain=cookie_domain,
        cookie_samesite=cookie_samesite,
        cors_origins=cors_origins,
        video_library_path=video_library_path,
        stream_chunk_size=stream_chunk_size,
    )


# PUBLIC_INTERFACE
def resolve_sqlite_path() -> Path:
    """Resolve a deterministic SQLite database file path if DATABASE_URL is not used."""
    settings = get_settings()
    if settings.sqlite_path:
        return Path(settings.sqlite_path)

    # Deterministic default location inside the backend container root.
    # Keep it stable across environments unless overridden.
    return Path(__file__).resolve().parents[2] / "data" / "streamflix.db"


# PUBLIC_INTERFACE
def resolve_database_url() -> str:
    """Resolve SQLAlchemy database URL from DATABASE_URL or SQLITE_PATH/default path."""
    settings = get_settings()
    if settings.database_url:
        return settings.database_url

    db_path = resolve_sqlite_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Ensure absolute path for sqlite URL. (Four slashes means absolute path.)
    absolute = db_path.resolve()
    return f"sqlite:///{absolute}"
