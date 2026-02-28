from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case
from datetime import datetime, timedelta
from typing import List, Optional
from app.models.usage_metric import UsageMetric
from app.models.api import API
from app.schemas.analytics import (
    UsageStatsResponse,
    EndpointStatsResponse,
    ErrorStatsResponse,
    PerformanceStatsResponse
)

def get_usage_stats(
    db: Session,
    api_id: int,
    user_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Optional[UsageStatsResponse]:
    api = db.query(API).filter(API.id == api_id, API.user_id == user_id).first()
    if not api:
        return None
    
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=7)
    if not end_date:
        end_date = datetime.utcnow()
    
    query = db.query(
        func.count(UsageMetric.id).label('total_requests'),
        func.count(case((UsageMetric.status_code < 400, 1))).label('successful_requests'),
        func.count(case((UsageMetric.status_code >= 400, 1))).label('failed_requests'),
        func.avg(UsageMetric.response_time_ms).label('avg_response_time_ms')
    ).filter(
        and_(
            UsageMetric.api_id == api_id,
            UsageMetric.timestamp >= start_date,
            UsageMetric.timestamp <= end_date
        )
    )
    
    result = query.first()
    
    return UsageStatsResponse(
        api_id=api_id,
        total_requests=result.total_requests or 0,
        successful_requests=result.successful_requests or 0,
        failed_requests=result.failed_requests or 0,
        avg_response_time_ms=float(result.avg_response_time_ms or 0),
        period_start=start_date,
        period_end=end_date
    )

def get_endpoint_stats(
    db: Session,
    api_id: int,
    user_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 10
) -> List[EndpointStatsResponse]:
    api = db.query(API).filter(API.id == api_id, API.user_id == user_id).first()
    if not api:
        return []
    
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=7)
    if not end_date:
        end_date = datetime.utcnow()
    
    query = db.query(
        UsageMetric.endpoint,
        UsageMetric.method,
        func.count(UsageMetric.id).label('request_count'),
        func.avg(UsageMetric.response_time_ms).label('avg_response_time_ms'),
        (func.count(case((UsageMetric.status_code < 400, 1))) * 100.0 / func.count(UsageMetric.id)).label('success_rate')
    ).filter(
        and_(
            UsageMetric.api_id == api_id,
            UsageMetric.timestamp >= start_date,
            UsageMetric.timestamp <= end_date
        )
    ).group_by(
        UsageMetric.endpoint,
        UsageMetric.method
    ).order_by(
        func.count(UsageMetric.id).desc()
    ).limit(limit)
    
    results = query.all()
    
    return [
        EndpointStatsResponse(
            endpoint=r.endpoint,
            method=r.method,
            request_count=r.request_count,
            avg_response_time_ms=float(r.avg_response_time_ms or 0),
            success_rate=float(r.success_rate or 0)
        )
        for r in results
    ]

def get_error_stats(
    db: Session,
    api_id: int,
    user_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[ErrorStatsResponse]:
    api = db.query(API).filter(API.id == api_id, API.user_id == user_id).first()
    if not api:
        return []
    
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=7)
    if not end_date:
        end_date = datetime.utcnow()
    
    total_errors_query = db.query(
        func.count(UsageMetric.id)
    ).filter(
        and_(
            UsageMetric.api_id == api_id,
            UsageMetric.status_code >= 400,
            UsageMetric.timestamp >= start_date,
            UsageMetric.timestamp <= end_date
        )
    ).scalar()
    
    if not total_errors_query or total_errors_query == 0:
        return []
    
    query = db.query(
        UsageMetric.status_code,
        func.count(UsageMetric.id).label('error_count'),
        func.max(UsageMetric.endpoint).label('sample_endpoint')
    ).filter(
        and_(
            UsageMetric.api_id == api_id,
            UsageMetric.status_code >= 400,
            UsageMetric.timestamp >= start_date,
            UsageMetric.timestamp <= end_date
        )
    ).group_by(
        UsageMetric.status_code
    ).order_by(
        func.count(UsageMetric.id).desc()
    )
    
    results = query.all()
    
    return [
        ErrorStatsResponse(
            status_code=r.status_code,
            error_count=r.error_count,
            percentage=float((r.error_count * 100.0) / total_errors_query),
            sample_endpoint=r.sample_endpoint
        )
        for r in results
    ]

def get_performance_stats(
    db: Session,
    api_id: int,
    user_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Optional[PerformanceStatsResponse]:
    api = db.query(API).filter(API.id == api_id, API.user_id == user_id).first()
    if not api:
        return None
    
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=7)
    if not end_date:
        end_date = datetime.utcnow()
    
    query = db.query(
        func.min(UsageMetric.response_time_ms).label('min_response_time_ms'),
        func.max(UsageMetric.response_time_ms).label('max_response_time_ms'),
        func.avg(UsageMetric.response_time_ms).label('avg_response_time_ms')
    ).filter(
        and_(
            UsageMetric.api_id == api_id,
            UsageMetric.timestamp >= start_date,
            UsageMetric.timestamp <= end_date
        )
    )
    
    result = query.first()
    
    if not result or result.min_response_time_ms is None:
        return None
    
    return PerformanceStatsResponse(
        api_id=api_id,
        min_response_time_ms=float(result.min_response_time_ms),
        max_response_time_ms=float(result.max_response_time_ms),
        avg_response_time_ms=float(result.avg_response_time_ms)
    )
