from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.api import API
from app.models.user import User
from app.utils.logger import api_logger

def create_api(
    db: Session,
    user: User,
    name: str,
    base_url: str,
    auth_type: str,
    description: Optional[str] = None,
    auth_config: Optional[dict] = None
) -> API:
    api_logger.info(f"Creating API: name={name}, user_id={user.id}, base_url={base_url}")
    
    api = API(
        name=name,
        description=description,
        base_url=str(base_url),
        auth_type=auth_type,
        auth_config=auth_config,
        user_id=user.id,
        is_active=True
    )

    db.add(api)
    db.commit()
    db.refresh(api)
    
    api_logger.info(f"API created successfully: api_id={api.id}, name={name}, user_id={user.id}")
    return api

def get_user_apis(db: Session, user: User) -> List[API]:
    api_logger.info(f"Fetching APIs for user_id: {user.id}")
    apis = db.query(API).filter(API.user_id == user.id).all()
    api_logger.info(f"Found {len(apis)} APIs for user_id: {user.id}")
    return apis

def get_api_by_id(db: Session, api_id: int, user: User) -> Optional[API]:
    api_logger.info(f"Fetching API: api_id={api_id}, user_id={user.id}")
    
    api = db.query(API).filter(
        API.id == api_id,
        API.user_id == user.id
    ).first()
    
    if api:
        api_logger.info(f"API found: api_id={api_id}, name={api.name}")
    else:
        api_logger.warning(f"API not found or access denied: api_id={api_id}, user_id={user.id}")
    
    return api

def update_api(
    db: Session,
    api: API,
    name: Optional[str] = None,
    description: Optional[str] = None,
    base_url: Optional[str] = None,
    auth_type: Optional[str] = None,
    auth_config: Optional[dict] = None,
    is_active: Optional[bool] = True
) -> API:
    api_logger.info(f"Updating API: api_id={api.id}, name={api.name}")
    
    if name is not None:
        api.name = name
    if description is not None:
        api.description = description
    if base_url is not None:
        api.base_url = base_url
    if auth_type is not None:
        api.auth_type = auth_type
    if auth_config is not None:
        api.auth_config = auth_config
    if is_active is not None:
        api.is_active = is_active

    db.commit()
    db.refresh(api)
    
    api_logger.info(f"API updated successfully: api_id={api.id}, name={api.name}")
    return api

def delete_api(db: Session, api: API) -> None:
    api_logger.info(f"Deleting API: api_id={api.id}, name={api.name}")
    
    db.delete(api)
    db.commit()
    
    api_logger.info(f"API deleted successfully: api_id={api.id}")