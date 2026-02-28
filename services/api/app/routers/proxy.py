import time
import httpx
from fastapi import APIRouter, Depends, HTTPException, Header, Request, status
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.models.api_key import APIKey
from app.models.api import API
from app.models.usage_metric import UsageMetric
from app.services import api_key_service, rate_limit_service
from app.utils.logger import api_logger

router = APIRouter(prefix="/proxy", tags=["Proxy"])

async def get_api_key_from_header(
    x_api_key: str = Header(..., description="API Key for authentication"),
    db: Session = Depends(get_db)
) -> APIKey:
    if not x_api_key:
        api_logger.warning("Missing API key in request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required"
        )
    
    api_key = api_key_service.verify_api_key(db=db, api_key=x_api_key)
    
    if not api_key:
        api_logger.warning(f"Invalid or expired API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API key"
        )
    
    return api_key

def track_usage(
    db: Session,
    api_id: int,
    endpoint: str,
    method: str,
    status_code: int,
    response_time_ms: float
):
    try:
        metric = UsageMetric(
            api_id=api_id,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time_ms=response_time_ms
        )
        db.add(metric)
        db.commit()
        api_logger.info(f"Usage tracked: api_id={api_id}, endpoint={endpoint}, status={status_code}, time={response_time_ms}ms")
    except Exception as e:
        api_logger.error(f"Failed to track usage: {str(e)}")
        db.rollback()

def add_auth_headers(headers: dict, api: API) -> dict:
    if api.auth_type == "bearer" and api.auth_config:
        token = api.auth_config.get("token")
        if token:
            headers["Authorization"] = f"Bearer {token}"
    
    elif api.auth_type == "api_key" and api.auth_config:
        key_name = api.auth_config.get("key_name", "X-API-Key")
        key_value = api.auth_config.get("key_value")
        if key_value:
            headers[key_name] = key_value
    
    elif api.auth_type == "basic" and api.auth_config:
        username = api.auth_config.get("username")
        password = api.auth_config.get("password")
        if username and password:
            import base64
            credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
            headers["Authorization"] = f"Basic {credentials}"
    
    return headers

@router.api_route("/{api_id}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_request(
    api_id: int,
    path: str,
    request: Request,
    api_key: APIKey = Depends(get_api_key_from_header),
    db: Session = Depends(get_db)
):
    start_time = time.time()
    
    api_logger.info(f"Proxy request: api_id={api_id}, path={path}, method={request.method}, user_id={api_key.user_id}")

    is_allowed, rate_limit_info = rate_limit_service.check_rate_limit(
        db=db,
        api_id=api_id,
        api_key_id=api_key.id
    )

    if not is_allowed and rate_limit_info:
        api_logger.warning(f"Rate limit exceeded for api_id={api_id}, key_id={api_key.id}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={
                "X-RateLimit-Limit-Hour": str(rate_limit_info["limit_hour"]),
                "X-RateLimit-Remaining-Hour": str(rate_limit_info["remaining_hour"]),
                "X-RateLimit-Reset-Hour": str(rate_limit_info["reset_hour"]),
                "X-RateLimit-Limit-Day": str(rate_limit_info["limit_day"]),
                "X-RateLimit-Remaining-Day": str(rate_limit_info["remaining_day"]),
                "X-RateLimit-Reset-Day": str(rate_limit_info["reset_day"]),
                "Retry-After": str(rate_limit_info["reset_hour"] - int(time.time()))
            }
        )

    api = db.query(API).filter(
        API.id == api_id,
        API.user_id == api_key.user_id
    ).first()
    
    if not api:
        api_logger.warning(f"API not found or access denied: api_id={api_id}, user_id={api_key.user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API not found"
        )
    
    if not api.is_active:
        api_logger.warning(f"API is inactive: api_id={api_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API is inactive"
        )
    
    target_url = f"{api.base_url.rstrip('/')}/{path.lstrip('/')}"
    
    headers = dict(request.headers)
    headers.pop("host", None)
    headers.pop("x-api-key", None)

    headers = add_auth_headers(headers, api)
    
    body = await request.body()
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                params=request.query_params,
                content=body
            )
        
        response_time_ms = (time.time() - start_time) * 1000

        track_usage(
            db=db,
            api_id=api_id,
            endpoint=f"/{path}",
            method=request.method,
            status_code=response.status_code,
            response_time_ms=response_time_ms
        )

        excluded_headers = {
            "content-length",
            "content-encoding",
            "transfer-encoding",
            "connection"
        }
        response_headers = {
            k: v for k, v in response.headers.items()
            if k.lower() not in excluded_headers
        }
        
        if rate_limit_info:
            response_headers["X-RateLimit-Limit-Hour"] = str(rate_limit_info["limit_hour"])
            response_headers["X-RateLimit-Remaining-Hour"] = str(rate_limit_info["remaining_hour"])
            response_headers["X-RateLimit-Reset-Hour"] = str(rate_limit_info["reset_hour"])
            response_headers["X-RateLimit-Limit-Day"] = str(rate_limit_info["limit_day"])
            response_headers["X-RateLimit-Remaining-Day"] = str(rate_limit_info["remaining_day"])
            response_headers["X-RateLimit-Reset-Day"] = str(rate_limit_info["reset_day"])
        
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=response_headers,
            media_type=response.headers.get("content-type")
        )
        
    except httpx.TimeoutException:
        response_time_ms = (time.time() - start_time) * 1000
        track_usage(db, api_id, f"/{path}", request.method, 504, response_time_ms)
        api_logger.error(f"Timeout proxying to {target_url}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Upstream API timeout"
        )
    
    except httpx.RequestError as e:
        response_time_ms = (time.time() - start_time) * 1000
        track_usage(db, api_id, f"/{path}", request.method, 502, response_time_ms)
        api_logger.error(f"Error proxying to {target_url}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to connect to upstream API"
        )
