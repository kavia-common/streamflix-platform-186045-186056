from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, EmailStr


# PUBLIC_INTERFACE
class UserCreate(BaseModel):
    """Schema for user registration request."""
    email: EmailStr = Field(..., description="User email (unique).")
    password: str = Field(..., min_length=6, description="User password (min length 6).")


# PUBLIC_INTERFACE
class UserLogin(BaseModel):
    """Schema for user login request."""
    email: EmailStr = Field(..., description="User email.")
    password: str = Field(..., description="User password.")


# PUBLIC_INTERFACE
class UserOut(BaseModel):
    """Public-facing user information."""
    id: int = Field(..., description="User ID.")
    email: EmailStr = Field(..., description="User email.")


# PUBLIC_INTERFACE
class TokenOut(BaseModel):
    """JWT token response (if returned in body, though cookies are used primarily)."""
    access_token: str = Field(..., description="JWT access token.")
    token_type: str = Field(default="bearer", description="Token type.")


# PUBLIC_INTERFACE
class VideoOut(BaseModel):
    """Public-facing video metadata."""
    id: int = Field(..., description="Video ID.")
    title: str = Field(..., description="Video title.")
    description: Optional[str] = Field(None, description="Video description.")
    duration_seconds: Optional[int] = Field(None, description="Duration in seconds.")
    filename: str = Field(..., description="Media file name under MEDIA_DIR.")
    thumbnail: Optional[str] = Field(None, description="Thumbnail file path or URL.")
    tags: Optional[List[str]] = Field(default=None, description="List of tags.")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp.")


# PUBLIC_INTERFACE
class HistoryCreate(BaseModel):
    """Schema for creating/upserting a watch history record."""
    video_id: int = Field(..., description="ID of the video watched.")
    position_seconds: int = Field(..., ge=0, description="Playback position in seconds.")


# PUBLIC_INTERFACE
class HistoryOut(BaseModel):
    """Public-facing watch history entry."""
    id: int = Field(..., description="History entry ID.")
    user_id: int = Field(..., description="User ID.")
    video_id: int = Field(..., description="Video ID.")
    position_seconds: int = Field(..., ge=0, description="Playback position in seconds.")
    updated_at: datetime = Field(..., description="Last update timestamp.")
