from pydantic import BaseModel, HttpUrl, field_validator
from datetime import datetime
from typing import Optional, List

class WebhookSubscriptionCreate(BaseModel):
    api_id: int
    event_type: str
    callback_url: HttpUrl
    secret: Optional[str] = None
    is_active: bool = True

    @field_validator('event_type')
    @classmethod
    def validate_event_type(cls, v):
        allowed_events = ['api.request', 'api.error', 'api.rate_limit', 'api.key.created', 'api.key.revoked']
        if v not in allowed_events:
            raise ValueError(f'event_type must be one of {allowed_events}')
        return v

class WebhookSubscriptionUpdate(BaseModel):
    callback_url: Optional[HttpUrl] = None
    secret: Optional[str] = None
    is_active: Optional[bool] = None

class WebhookSubscriptionResponse(BaseModel):
    id: int
    api_id: int
    event_type: str
    callback_url: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class WebhookDeliveryResponse(BaseModel):
    id: int
    subscription_id: int
    event_type: str
    payload: dict
    status: str
    response_code: Optional[int] = None
    response_body: Optional[str] = None
    attempt_count: int
    created_at: datetime
    delivered_at: Optional[datetime] = None

    class Config:
        from_attributes = True
