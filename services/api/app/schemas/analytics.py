from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UsageStatsResponse(BaseModel):
    api_id: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time_ms: float
    period_start: datetime
    period_end: datetime

class EndpointStatsResponse(BaseModel):
    endpoint: str
    method: str
    request_count: int
    avg_response_time_ms: float
    success_rate: float

class ErrorStatsResponse(BaseModel):
    status_code: int
    error_count: int
    percentage: float
    sample_endpoint: Optional[str] = None

class PerformanceStatsResponse(BaseModel):
    api_id: int
    min_response_time_ms: float
    max_response_time_ms: float
    avg_response_time_ms: float
    p50_response_time_ms: Optional[float] = None
    p95_response_time_ms: Optional[float] = None
    p99_response_time_ms: Optional[float] = None
