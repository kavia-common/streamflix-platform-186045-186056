from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository


class AuthService:
    """Business logic for authentication and user management."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._users = UserRepository(db)

    def register(self, email: str, password: str) -> User:
        existing = self._users.get_by_email(email)
        if existing:
            raise ValueError("Email is already registered")

        user = self._users.create(email=email, password_hash=hash_password(password))
        self._db.commit()
        self._db.refresh(user)
        return user

    def authenticate(self, email: str, password: str) -> User:
        user = self._users.get_by_email(email)
        if not user:
            raise ValueError("Invalid credentials")

        if not verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials")

        return user

    def issue_token(self, user: User) -> str:
        return create_access_token(subject=str(user.id), extra_claims={"email": user.email})
