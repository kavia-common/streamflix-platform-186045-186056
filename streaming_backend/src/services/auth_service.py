from typing import Optional, Dict, Any

from fastapi import HTTPException, status

from src.core.security import hash_password, verify_password, create_access_token
from src.data.repositories.base import UserRepository


class AuthService:
    """Business logic for authentication."""

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    # PUBLIC_INTERFACE
    def register(self, email: str, password: str) -> Dict[str, Any]:
        """Register a new user."""
        existing = self.user_repo.get_user_by_email(email)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        pwd_hash = hash_password(password)
        user = self.user_repo.create_user(email=email, password_hash=pwd_hash)
        return user

    # PUBLIC_INTERFACE
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Validate credentials and create access token."""
        user = self.user_repo.get_user_by_email(email)
        if not user or not verify_password(password, user["password_hash"]):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        token = create_access_token(subject=str(user["id"]), additional_claims={"email": user["email"]})
        return {"user": user, "token": token}

    # PUBLIC_INTERFACE
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a user by id."""
        return self.user_repo.get_user_by_id(user_id)
