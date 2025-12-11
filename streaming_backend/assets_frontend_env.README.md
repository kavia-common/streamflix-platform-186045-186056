Create or verify the following file in the streaming_frontend container for local dev:

Filename: streaming_frontend/.env.development
Contents:
REACT_APP_API_BASE=http://localhost:3001

Notes:
- Frontend should send requests with credentials: 'include' to work with cookie auth.
- If you run frontend on a non-default origin, set REACT_APP_FRONTEND_URL in backend env to that exact origin so CORS allows it.
