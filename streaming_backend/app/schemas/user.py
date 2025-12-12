from __future__ import annotations

from pydantic import Field

from app.schemas.common import APIModel


class UserOut(APIModel):
    id: int = Field(..., description="User id")
    email: str = Field(..., description="User email")
