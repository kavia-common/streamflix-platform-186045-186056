from __future__ import annotations

from pydantic import Field

from app.schemas.common import APIModel


class RegisterRequest(APIModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")


class LoginRequest(APIModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class AuthUser(APIModel):
    id: int = Field(..., description="User id")
    email: str = Field(..., description="User email")


class AuthResponse(APIModel):
    user: AuthUser = Field(..., description="Authenticated user data")
