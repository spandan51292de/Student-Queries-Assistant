from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Union

from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions import CredentialsException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


def create_access_token(
    subject: Union[str, Any], expires_delta: Union[timedelta, None] = None
) -> str:
    """Generate a JWT access token for a given user ID."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    
    return jwt.encode(
        to_encode, 
        settings.SECRET_KEY.get_secret_value(), 
        algorithm=ALGORITHM
    )


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decodes and verifies a JWT.
    Raises domain-specific exceptions if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY.get_secret_value(), 
            algorithms=[ALGORITHM]
        )
        return payload
    except ExpiredSignatureError:
        raise CredentialsException(message="Your session has expired. Please log in again.")
    except JWTError:
        raise CredentialsException(message="Could not validate credentials. The token is invalid.")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a raw password against its stored hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a raw password for database storage."""
    return pwd_context.hash(password)