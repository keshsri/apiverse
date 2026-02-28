from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List
from app.core.database import get_db
from app.models.user import User
from app.schemas.analytics import (
    UsageStatsResponse,
    EndpointStatsResponse,
    ErrorStatsResponse,
    PerformanceStatsResponse
)
from app.services import analytics_service
from app.utils.dependencies import get_current_user
from app.utils.logger import api_logger

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/{api_id}/usage", response_model=UsageStatsResponse)
def get_usage_stats(
    api_id: int,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    api_logger.info(f"Get usage stats for api_id={api_id}, user_id={current_user.id}")
    
    stats = analytics_service.get_usage_stats(
        db=db,
        api_id=api_id,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API not found"
        )
    
    return stats

@router.get("/{api_id}/endpoints", response_model=List[EndpointStatsResponse])
def get_endpoint_stats(
    api_id: int,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    api_logger.info(f"Get endpoint stats for api_id={api_id}, user_id={current_user.id}")
    
    stats = analytics_service.get_endpoint_stats(
        db=db,
        api_id=api_id,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )
    
    return stats

@router.get("/{api_id}/errors", response_model=List[ErrorStatsResponse])
def get_error_stats(
    api_id: int,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    api_logger.info(f"Get error stats for api_id={api_id}, user_id={current_user.id}")
    
    stats = analytics_service.get_error_stats(
        db=db,
        api_id=api_id,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    
    return stats

@router.get("/{api_id}/performance", response_model=PerformanceStatsResponse)
def get_performance_stats(
    api_id: int,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    api_logger.info(f"Get performance stats for api_id={api_id}, user_id={current_user.id}")
    
    stats = analytics_service.get_performance_stats(
        db=db,
        api_id=api_id,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API not found or no data available"
        )
    
    return stats
