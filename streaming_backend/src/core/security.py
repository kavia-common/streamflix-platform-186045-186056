from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

import bcrypt
import jwt

from src.core.config import SECRET_KEY, TOKEN_EXPIRE_MIN

ALGORITHM = "HS256"
AUTH_COOKIE_NAME = "access_token"


# PUBLIC_INTERFACE
def hash_password(plain_password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain_password.encode("utf-8"), salt).decode("utf-8")


# PUBLIC_INTERFACE
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


# PUBLIC_INTERFACE
def create_access_token(subject: str, additional_claims: Optional[Dict[str, Any]] = None) -> str:
    """Create a JWT access token with expiration."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=TOKEN_EXPIRE_MIN)
    to_encode: Dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "type": "access",
    }
    if additional_claims:
        to_encode.update(additional_claims)
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# PUBLIC_INTERFACE
def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify a JWT token and return its payload or None."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None
