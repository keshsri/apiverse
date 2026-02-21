from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class AuthType(str, Enum):
    NONE = "none"
    BEARER = "bearer"
    API_KEY = "api_key"
    BASIC = "basic"
    CUSTOM = "custom"

class APICreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    base_url: HttpUrl
    auth_type: AuthType = AuthType.NONE
    auth_config: Optional[dict] = None

class APIUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    base_url: Optional[HttpUrl] = None
    auth_type: Optional[AuthType] = None
    auth_config: Optional[dict] = None
    is_active: Optional[bool] = None

class APIResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    base_url: str
    auth_type: str
    is_active: bool
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class APIListResponse(BaseModel):
    total: int
    apis: list[APIResponse]