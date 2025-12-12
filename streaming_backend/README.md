# streaming_backend

FastAPI backend for StreamFlix (auth, videos, history, HTTP Range streaming) using SQLite.

## Run (dev)

1. Ensure `.env` contains at least `JWT_SECRET` and a CORS origin that matches your frontend.
2. Start:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 3001
```

## Seed videos

Place video files under `VIDEO_LIBRARY_PATH` (default: `media/`) and run:

```bash
python -m scripts.seed
```

The seed is idempotent (won't insert duplicates for the same file_path).
"""
