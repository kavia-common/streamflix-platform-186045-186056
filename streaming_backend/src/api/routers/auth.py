from typing import Any

from fastapi import APIRouter, Depends, Response, status

from src.core.config import COOKIE_SECURE, COOKIE_DOMAIN, COOKIE_SAMESITE
from src.core.dependencies import get_current_user
from src.core.security import AUTH_COOKIE_NAME
from src.domain.models import UserCreate, UserLogin, UserOut
from src.core.di import get_auth_service
from src.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", summary="Register", description="Register a new user account.", response_model=UserOut,
             responses={400: {"description": "Email already registered"}})
def register(payload: UserCreate, auth_service: AuthService = Depends(get_auth_service)) -> Any:
    """Register a new user with email and password."""
    user = auth_service.register(email=str(payload.email), password=payload.password)
    return {"id": user["id"], "email": user["email"]}


@router.post("/login", summary="Login", description="Login and set JWT cookie.", response_model=UserOut,
             responses={401: {"description": "Invalid credentials"}})
def login(payload: UserLogin, response: Response, auth_service: AuthService = Depends(get_auth_service)) -> Any:
    """Login user, set JWT cookie, and return user."""
    result = auth_service.login(email=str(payload.email), password=payload.password)
    token = result["token"]
    user = result["user"]
    response.set_cookie(
        key=AUTH_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,  # 'lax' or 'none'
        domain=COOKIE_DOMAIN,
        path="/",
        max_age=None,
    )
    return {"id": user["id"], "email": user["email"]}


@router.post("/logout", summary="Logout", description="Clear JWT cookie.", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> None:
    """Logout by clearing the auth cookie."""
    response.delete_cookie(
        key=AUTH_COOKIE_NAME,
        domain=COOKIE_DOMAIN,
        path="/",
    )
    return None


@router.get("/me", summary="Current User", description="Get information about the authenticated user.", response_model=UserOut)
def me(user=Depends(get_current_user)) -> Any:
    """Return current authenticated user."""
    return {"id": user["id"], "email": user["email"]}
