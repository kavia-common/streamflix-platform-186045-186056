from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest
from app.schemas.user import UserOut
from app.services.auth_service import AuthService
from app.core.dependencies import get_current_user_from_request

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=AuthResponse,
    summary="Register a new user",
    description="Creates a new user and returns the user object. Does not automatically log in.",
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> AuthResponse:
    service = AuthService(db)
    try:
        user = service.register(email=payload.email, password=payload.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    return AuthResponse(user=UserOut.model_validate(user))


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Login",
    description="Authenticates a user and sets an HttpOnly JWT cookie for subsequent requests.",
)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> AuthResponse:
    service = AuthService(db)
    try:
        user = service.authenticate(email=payload.email, password=payload.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e

    token = service.issue_token(user)
    settings = get_settings()

    response.set_cookie(
        key=settings.jwt_cookie_name,
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        domain=settings.cookie_domain,
        path="/",
        max_age=settings.jwt_expires_minutes * 60,
    )

    return AuthResponse(user=UserOut.model_validate(user))


@router.post(
    "/logout",
    summary="Logout",
    description="Clears the JWT cookie.",
)
def logout(response: Response) -> dict:
    settings = get_settings()
    response.delete_cookie(
        key=settings.jwt_cookie_name,
        domain=settings.cookie_domain,
        path="/",
    )
    return {"ok": True}


@router.get(
    "/me",
    response_model=UserOut,
    summary="Get current user",
    description="Returns the currently authenticated user based on the JWT cookie.",
)
def me(request: Request, db: Session = Depends(get_db)) -> UserOut:
    user = get_current_user_from_request(request, db)
    return UserOut(id=user["id"], email=user["email"])
