from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class APIModel(BaseModel):
    """Base Pydantic model with consistent API defaults."""

    model_config = ConfigDict(from_attributes=True)
