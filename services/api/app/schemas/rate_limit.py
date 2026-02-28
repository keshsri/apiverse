from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class RateLimitCreateRequest(BaseModel):
    api_id: int
    tier: str = Field(default="standard", max_length=50)
    requests_per_hour: int = Field(default=1000, gt=0)
    requests_per_day: int = Field(default=10000, gt=0)

class RateLimitUpdateRequest(BaseModel):
    tier: Optional[str] = Field(None, max_length=50)
    requests_per_hour: Optional[int] = Field(None, gt=0)
    requests_per_day: Optional[int] = Field(None, gt=0)

class RateLimitResponse(BaseModel):
    id: int
    api_id: int
    tier: str
    requests_per_hour: int
    requests_per_day: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RateLimitStatus(BaseModel):
    limit_hour: int
    remaining_hour: int
    reset_hour: int
    limit_day: int
    remaining_day: int
    reset_day: int
