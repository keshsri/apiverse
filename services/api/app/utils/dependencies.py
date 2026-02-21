from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.config import get_settings
from app.utils.logger import security_logger

settings = get_settings()
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")

        if user_id is None:
            security_logger.warning("JWT token missing 'sub' claim")
            raise credentials_exception

    except JWTError as e:
        security_logger.warning(f"JWT validation failed: {str(e)}")
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()

    if user is None:
        security_logger.warning(f"User not found for user_id: {user_id}")
        raise credentials_exception

    if not user.is_active:
        security_logger.warning(f"Inactive user attempted access: user_id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    security_logger.info(f"User authenticated successfully: user_id={user.id}, email={user.email}")
    return user