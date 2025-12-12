from __future__ import annotations

from fastapi import Cookie, Depends, HTTPException, status
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import decode_access_token
from app.db.session import get_db
from app.repositories.user_repository import UserRepository


# PUBLIC_INTERFACE
def get_current_user(
    db: Session = Depends(get_db),
    token: str | None = Cookie(default=None, alias=None),
) -> dict:
    """Return the current user (dict with id/email) based on JWT stored in an HttpOnly cookie.

    Notes:
      - We read the cookie using the configured JWT_COOKIE_NAME at runtime. Since FastAPI's
        Cookie dependency uses a static name, we manually read from request cookies in router code.
        This dependency is retained for compatibility but not used directly.
    """
    raise NotImplementedError(
        "Use get_current_user_from_request(request, db) instead. "
        "Cookie name is dynamic via env."
    )


# PUBLIC_INTERFACE
def get_current_user_from_request(request, db: Session) -> dict:
    """Resolve current user from the configured JWT cookie in the incoming request."""
    settings = get_settings()
    token_value = request.cookies.get(settings.jwt_cookie_name)
    if not token_value:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        payload = decode_access_token(token_value)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_id = int(sub)
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return {"id": user.id, "email": user.email}
