from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.utils.security import hash_password, verify_password
from app.utils.logger import auth_logger

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    auth_logger.info(f"Authentication attempt for email: {email}")
    
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        auth_logger.warning(f"Authentication failed: User not found - {email}")
        return None
    
    if not verify_password(password, user.hashed_password):
        auth_logger.warning(f"Authentication failed: Invalid password - {email}")
        return None
    
    auth_logger.info(f"Authentication successful for user_id: {user.id}, email: {email}")
    return user

def create_user(db: Session, email: str, password: str, full_name: Optional[str] = None) -> User:
    auth_logger.info(f"Creating new user: {email}")
    
    hashed_password = hash_password(password)
    
    user = User(
        email=email,
        hashed_password=hashed_password,
        full_name=full_name,
        is_active=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    auth_logger.info(f"User created successfully: user_id={user.id}, email={email}")
    return user
