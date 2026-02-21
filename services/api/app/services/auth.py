from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.utils.security import hash_password, verify_password

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user

def create_user(db: Session, email: str, password: str, full_name: Optional[str] = None) -> User:
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
    
    return user
