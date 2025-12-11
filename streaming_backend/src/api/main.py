import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers.auth import router as auth_router
from src.api.routers.videos import router as videos_router
from src.api.routers.history import router as history_router

openapi_tags = [
    {"name": "Health", "description": "Health and status endpoints"},
    {"name": "Auth", "description": "User authentication and session"},
    {"name": "Videos", "description": "Video metadata and streaming"},
    {"name": "History", "description": "User watch history"},
]

app = FastAPI(
    title="StreamFlix Backend API",
    description="Backend API for authentication, video metadata, watch history, and video streaming with HTTP Range support.",
    version="1.0.0",
    openapi_tags=openapi_tags,
)

# Determine allowed CORS origins. For local dev, default to React app on 3000.
frontend_origin = os.getenv("REACT_APP_FRONTEND_URL") or os.getenv("FRONTEND_ORIGIN") or "http://localhost:3000"
allowed_origins = [frontend_origin]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,  # allow cookies for auth
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"], summary="Health Check", description="Returns API health status.")
def health_check():
    """Health check endpoint to verify the API is running."""
    return {"message": "Healthy"}


# Register routers
app.include_router(auth_router)
app.include_router(videos_router)
app.include_router(history_router)
