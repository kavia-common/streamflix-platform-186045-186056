from __future__ import annotations

"""
Seed the StreamFlix database idempotently by creating tables and scanning VIDEO_LIBRARY_PATH.

Usage:
  python -m scripts.seed
"""

from app.db.init_db import init_db


# PUBLIC_INTERFACE
def main() -> None:
    """Run idempotent DB initialization + seeding."""
    init_db()
    print("Seed completed.")


if __name__ == "__main__":
    main()
