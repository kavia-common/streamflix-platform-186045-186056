from typing import Dict, Any

from fastapi import Depends, HTTPException, status, Request

from src.core.security import verify_token, AUTH_COOKIE_NAME
from src.core.di import get_auth_service
from src.services.auth_service import AuthService


# PUBLIC_INTERFACE
def get_current_user(request: Request, auth_service: AuthService = Depends(get_auth_service)) -> Dict[str, Any]:
    """FastAPI dependency to extract current user from JWT cookie."""
    token = request.cookies.get(AUTH_COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    user = auth_service.get_user_by_id(int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
