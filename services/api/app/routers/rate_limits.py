from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.schemas.rate_limit import (
    RateLimitCreateRequest,
    RateLimitUpdateRequest,
    RateLimitResponse
)
from app.services import rate_limit_service
from app.utils.dependencies import get_current_user
from app.utils.logger import api_logger

router = APIRouter(prefix="/rate-limits", tags=["Rate Limits"])

@router.post("", response_model=RateLimitResponse, status_code=status.HTTP_201_CREATED)
def create_or_update_rate_limit(
    rate_limit_data: RateLimitCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    api_logger.info(f"Rate limit request for api_id={rate_limit_data.api_id}, user_id={current_user.id}")
    
    try:
        rate_limit = rate_limit_service.create_rate_limit(
            db=db,
            api_id=rate_limit_data.api_id,
            user=current_user,
            tier=rate_limit_data.tier,
            requests_per_hour=rate_limit_data.requests_per_hour,
            requests_per_day=rate_limit_data.requests_per_day
        )
        return rate_limit
    except ValueError as e:
        api_logger.warning(f"Rate limit creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        api_logger.error(f"Rate limit creation error: {str(e)}")
        raise

@router.get("/{api_id}", response_model=RateLimitResponse)
def get_rate_limit(
    api_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    api_logger.info(f"Get rate limit for api_id={api_id}, user_id={current_user.id}")
    
    rate_limit = rate_limit_service.get_rate_limit(db=db, api_id=api_id, user=current_user)
    
    if not rate_limit:
        rate_limit = rate_limit_service.get_or_create_rate_limit(db=db, api_id=api_id)
    
    return rate_limit
