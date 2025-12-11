# streamflix-platform-186045-186056

This workspace contains a multi-container streaming app:
- streaming_backend: FastAPI backend for auth, videos, history, and HTTP Range streaming.
- streaming_frontend: React (Vite + Tailwind) frontend.
- streaming_database: SQLite data storage; the backend also supports local SQLite by default.

Integration/wiring notes
- Backend CORS:
  - Credentials are enabled to support cookie-based auth.
  - The allowed origin is taken from REACT_APP_FRONTEND_URL (or FRONTEND_ORIGIN), defaulting to http://localhost:3000.
- Backend cookies:
  - For cross-site local dev, keep COOKIE_SAMESITE=lax and COOKIE_SECURE=false (or set appropriately for HTTPS).
- Backend database path (DB_PATH):
  - Priority: DB_PATH env > streaming_database/db_connection.txt > streaming_backend/data/app.db.
  - The backend auto-detects db_connection.txt in typical locations and normalizes sqlite/file URLs to absolute paths.
- Backend media location (MEDIA_DIR):
  - Defaults to streaming_backend/media. Seeded video filenames are relative to MEDIA_DIR.
  - Place sample media files (e.g., sample1.mp4, sample2.mp4) in this folder for streaming to work.
- Frontend environment:
  - Ensure a .env.development in the frontend with REACT_APP_API_BASE=http://localhost:3001
  - If using custom ports/hosts, set REACT_APP_FRONTEND_URL (or FRONTEND_ORIGIN) in backend env to match frontend origin.

Quick start (local)
1) Backend
   - Create a Python 3.12 venv and install requirements.txt.
   - Start uvicorn with port 3001 (e.g., uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --reload).
   - Optional: provide DB_PATH or ensure streaming_database/db_connection.txt exists.
   - Put your media files under streaming_backend/media matching filenames in DB (seed uses sample1.mp4 and sample2.mp4).

2) Frontend
   - In streaming_frontend, add .env.development with REACT_APP_API_BASE=http://localhost:3001
   - Start dev server (Vite default port 3000).

3) Auth and cookies
   - Because credentials are required, fetch calls from the frontend must include credentials: 'include'.
   - Make sure the browser is hitting the exact origin specified in backend CORS allowed origins.