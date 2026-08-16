from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.core.config import settings
from app.core.exceptions import BadRequestException, CredentialsException
from app.core.security import decode_access_token
from app.db.models.user import User
from app.schemas.auth import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    payload = decode_access_token(token)
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise CredentialsException(message="Token missing subject claim")
        
    try:
        token_data = TokenPayload(sub=int(user_id))
    except ValueError:
        raise CredentialsException(message="Invalid subject format in token")

    result = await db.execute(select(User).filter(User.id == token_data.sub))
    user = result.scalars().first()
    
    if user is None:
        raise CredentialsException(message="User not found")
        
    if not user.is_active:
        raise BadRequestException(message="Inactive user")
        
    return user