from datetime import datetime, timedelta, timezone
import bcrypt
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..config import settings
from ..database.mongodb import get_user_by_id

bearer = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except ValueError:
        return False

def create_access_token(user_id: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_minutes)
    return jwt.encode({'sub': user_id, 'exp': exp}, settings.jwt_secret, algorithm=settings.jwt_algorithm)

async def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)):
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication required')
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id = payload.get('sub')
        if not user_id:
            raise ValueError
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail='Invalid or expired token')
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail='User not found')
    return user
