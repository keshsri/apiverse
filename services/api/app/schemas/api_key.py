from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class Environment(str, Enum):
    test = "test"
    live = "live"

class APIKeyCreateRequest(BaseModel):
    name: Optional[str] = Field(None, max_length=255, description="Alias for the API Key")
    environment: Environment = Field(default=Environment.live, description="Test or live/prod environment")
    expires_in_days: Optional[int] = Field(None, gt=0, le=365, description="Key expiration in days (max 365)")

class APIKeyResponse(BaseModel):
    id: int
    key_prefix: str
    name: Optional[str]
    environment: str
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime]
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True

class APIKeyCreateResponse(BaseModel):
    id: int
    api_key: str
    key_prefix: str
    name: Optional[str]
    environment: str
    created_at: datetime
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True

class APIKeyListResponse(BaseModel):
    total: int
    api_keys: List[APIKeyResponse]