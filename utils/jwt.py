from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt

from core.config import settings


def create_access_token(
    subject: str,
    expires_minutes: Optional[int] = None
) -> str:
    """
    Create JWT access token.
    subject: user_id or guest_session_id
    """
    expire = datetime.utcnow() + timedelta(
        minutes=expires_minutes or settings.JWT_EXPIRE_MINUTES
    )

    payload = {
        "sub": subject,
        "exp": expire
    }

    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return token


def verify_access_token(token: str) -> Optional[str]:
    """
    Verify JWT and return subject.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload.get("sub")
    except JWTError:
        return None
