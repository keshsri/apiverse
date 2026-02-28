import time
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from app.models.rate_limit import RateLimit
from app.models.api import API
from app.models.user import User
from app.services.redis_service import redis_service
from app.utils.logger import api_logger

def get_or_create_rate_limit(db: Session, api_id: int) -> RateLimit:
    rate_limit = db.query(RateLimit).filter(RateLimit.api_id == api_id).first()
    
    if not rate_limit:
        api_logger.info(f"Creating default rate limit for api_id={api_id}")
        rate_limit = RateLimit(
            api_id=api_id,
            tier="standard",
            requests_per_hour=1000,
            requests_per_day=10000
        )
        db.add(rate_limit)
        db.commit()
        db.refresh(rate_limit)
    
    return rate_limit

def check_rate_limit(
    db: Session,
    api_id: int,
    api_key_id: int
) -> Tuple[bool, Optional[dict]]:
    rate_limit = get_or_create_rate_limit(db, api_id)
    redis_client = redis_service.get_client()
    
    current_time = int(time.time())
    hour_key = f"rate_limit:api:{api_id}:key:{api_key_id}:hour:{current_time // 3600}"
    day_key = f"rate_limit:api:{api_id}:key:{api_key_id}:day:{current_time // 86400}"
    
    try:
        hour_count = redis_client.get(hour_key)
        day_count = redis_client.get(day_key)
        
        hour_count = int(hour_count) if hour_count else 0
        day_count = int(day_count) if day_count else 0
        
        hour_exceeded = hour_count >= rate_limit.requests_per_hour
        day_exceeded = day_count >= rate_limit.requests_per_day
        
        if hour_exceeded or day_exceeded:
            api_logger.warning(
                f"Rate limit exceeded: api_id={api_id}, key_id={api_key_id}, "
                f"hour={hour_count}/{rate_limit.requests_per_hour}, "
                f"day={day_count}/{rate_limit.requests_per_day}"
            )
            
            hour_reset = ((current_time // 3600) + 1) * 3600
            day_reset = ((current_time // 86400) + 1) * 86400
            
            return False, {
                "limit_hour": rate_limit.requests_per_hour,
                "remaining_hour": max(0, rate_limit.requests_per_hour - hour_count),
                "reset_hour": hour_reset,
                "limit_day": rate_limit.requests_per_day,
                "remaining_day": max(0, rate_limit.requests_per_day - day_count),
                "reset_day": day_reset
            }
        
        pipe = redis_client.pipeline()
        pipe.incr(hour_key)
        pipe.expire(hour_key, 3600)
        pipe.incr(day_key)
        pipe.expire(day_key, 86400)
        pipe.execute()
        
        hour_reset = ((current_time // 3600) + 1) * 3600
        day_reset = ((current_time // 86400) + 1) * 86400
        
        rate_limit_info = {
            "limit_hour": rate_limit.requests_per_hour,
            "remaining_hour": rate_limit.requests_per_hour - hour_count - 1,
            "reset_hour": hour_reset,
            "limit_day": rate_limit.requests_per_day,
            "remaining_day": rate_limit.requests_per_day - day_count - 1,
            "reset_day": day_reset
        }
        
        api_logger.debug(
            f"Rate limit check passed: api_id={api_id}, key_id={api_key_id}, "
            f"hour={hour_count + 1}/{rate_limit.requests_per_hour}, "
            f"day={day_count + 1}/{rate_limit.requests_per_day}"
        )
        
        return True, rate_limit_info
        
    except Exception as e:
        api_logger.error(f"Redis error in rate limiting: {str(e)}")
        return True, None

def create_rate_limit(
    db: Session,
    api_id: int,
    user: User,
    tier: str,
    requests_per_hour: int,
    requests_per_day: int
) -> RateLimit:
    api = db.query(API).filter(API.id == api_id, API.user_id == user.id).first()
    if not api:
        raise ValueError("API not found or access denied")
    
    rate_limit = db.query(RateLimit).filter(RateLimit.api_id == api_id).first()
    
    if rate_limit:
        rate_limit.tier = tier
        rate_limit.requests_per_hour = requests_per_hour
        rate_limit.requests_per_day = requests_per_day
        api_logger.info(f"Updated rate limit for api_id={api_id}")
    else:
        rate_limit = RateLimit(
            api_id=api_id,
            tier=tier,
            requests_per_hour=requests_per_hour,
            requests_per_day=requests_per_day
        )
        db.add(rate_limit)
        api_logger.info(f"Created rate limit for api_id={api_id}")
    
    db.commit()
    db.refresh(rate_limit)
    return rate_limit

def get_rate_limit(db: Session, api_id: int, user: User) -> Optional[RateLimit]:
    api = db.query(API).filter(API.id == api_id, API.user_id == user.id).first()
    if not api:
        return None
    
    return db.query(RateLimit).filter(RateLimit.api_id == api_id).first()
