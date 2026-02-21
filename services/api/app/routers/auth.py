from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.database import get_db
from app.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse
from app.services.auth import create_user, authenticate_user
from app.utils.security import create_access_token
from app.utils.logger import auth_logger

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegisterRequest, db: Session = Depends(get_db)):
    auth_logger.info(f"Registration request for email: {user_data.email}")
    
    try:
        user = create_user(
            db=db,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )
        auth_logger.info(f"User registered successfully: user_id={user.id}, email={user_data.email}")
        return user
    
    except IntegrityError:
        db.rollback()
        auth_logger.warning(f"Registration failed: Email already exists - {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    except Exception as e:
        db.rollback()
        auth_logger.error(f"Registration error for {user_data.email}: {str(e)}")
        raise

@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLoginRequest, db: Session = Depends(get_db)):
    auth_logger.info(f"Login request for email: {credentials.email}")
    
    user = authenticate_user(db=db, email=credentials.email, password=credentials.password)
    
    if not user:
        auth_logger.warning(f"Login failed: Invalid credentials - {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        auth_logger.warning(f"Login failed: Inactive account - {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    auth_logger.info(f"Login successful: user_id={user.id}, email={credentials.email}")
    
    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )
