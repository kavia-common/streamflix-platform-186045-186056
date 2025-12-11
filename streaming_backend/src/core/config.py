import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load .env if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]

def _read_db_path_from_connection_file() -> Optional[str]:
    """
    Attempts to read a database path from db_connection.txt.
    Expected formats include:
      - sqlite:////absolute/path/to/file.db
      - file:/absolute/path/to/file.db
      - /absolute/path/to/file.db
    Returns a normalized absolute path string or None if not found.
    """
    # Search common locations for db_connection.txt
    candidates = [
        BASE_DIR / "db_connection.txt",
        BASE_DIR.parent / "db_connection.txt",
        BASE_DIR / "streaming_database" / "db_connection.txt",
    ]
    for candidate in candidates:
        if candidate.exists():
            try:
                content = candidate.read_text(encoding="utf-8").strip()
                # Normalize sqlite URL schemes
                if content.startswith("sqlite:///"):
                    # Remove sqlite scheme, keep absolute path
                    path = content.replace("sqlite:///", "/")
                elif content.startswith("sqlite://"):
                    # Rare case of two slashes
                    path = content.replace("sqlite://", "/")
                elif content.startswith("file:"):
                    path = content.replace("file:", "")
                else:
                    path = content
                return str(Path(path).expanduser().resolve())
            except Exception:
                return None
    return None

# Configuration values with environment overrides
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production")
# Token expiry in minutes
try:
    TOKEN_EXPIRE_MIN = int(os.getenv("TOKEN_EXPIRE_MIN", "120"))
except ValueError:
    TOKEN_EXPIRE_MIN = 120

# Cookies security flags
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() in {"1", "true", "yes"}
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "lax").lower()
COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN")  # Optional

# Media directory for video files
MEDIA_DIR = os.getenv("MEDIA_DIR", str(BASE_DIR / "media"))

# Database path handling with db_connection.txt fallback
DB_PATH = os.getenv("DB_PATH")
if not DB_PATH:
    DB_PATH = _read_db_path_from_connection_file()
if not DB_PATH:
    # Use default db under backend directory
    DB_PATH = str(BASE_DIR / "data" / "app.db")

# Ensure directories exist for defaults (media, data)
Path(MEDIA_DIR).mkdir(parents=True, exist_ok=True)
Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
