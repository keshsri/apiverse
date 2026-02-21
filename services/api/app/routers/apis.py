from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.user import User
from app.schemas.api import (
    APICreateRequest,
    APIUpdateRequest,
    APIResponse,
    APIListResponse
)
from app.services import api_service
from app.utils.dependencies import get_current_user
from app.utils.logger import api_logger

router = APIRouter(prefix="/apis", tags=["API Management"])

@router.post("", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
def create_api(
    api_data: APICreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    api_logger.info(f"API creation request: name={api_data.name}, user_id={current_user.id}")
    
    try:
        api = api_service.create_api(
            db=db,
            user=current_user,
            name=api_data.name,
            description=api_data.description,
            base_url=str(api_data.base_url),
            auth_type=api_data.auth_type.value,
            auth_config=api_data.auth_config
        )
        return api
    except Exception as e:
        api_logger.error(f"API creation failed for user_id={current_user.id}: {str(e)}")
        raise

@router.get("", response_model=APIListResponse)
def list_apis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    api_logger.info(f"Listing APIs for user_id: {current_user.id}")
    apis = api_service.get_user_apis(db=db, user=current_user)
    return APIListResponse(total=len(apis), apis=apis)

@router.get("/{api_id}", response_model=APIResponse)
def get_api(
    api_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    api_logger.info(f"Get API request: api_id={api_id}, user_id={current_user.id}")
    api = api_service.get_api_by_id(db=db, api_id=api_id, user=current_user)
    
    if not api:
        api_logger.warning(f"API not found: api_id={api_id}, user_id={current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API not found"
        )
    
    return api

@router.put("/{api_id}", response_model=APIResponse)
def update_api(
    api_id: int,
    api_data: APIUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    api_logger.info(f"Update API request: api_id={api_id}, user_id={current_user.id}")
    api = api_service.get_api_by_id(db=db, api_id=api_id, user=current_user)
    
    if not api:
        api_logger.warning(f"API not found for update: api_id={api_id}, user_id={current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API not found"
        )
    
    try:
        updated_api = api_service.update_api(
            db=db,
            api=api,
            name=api_data.name,
            description=api_data.description,
            base_url=str(api_data.base_url) if api_data.base_url else None,
            auth_type=api_data.auth_type.value if api_data.auth_type else None,
            auth_config=api_data.auth_config,
            is_active=api_data.is_active
        )
        return updated_api
    except Exception as e:
        api_logger.error(f"API update failed: api_id={api_id}, user_id={current_user.id}: {str(e)}")
        raise

@router.delete("/{api_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_api(
    api_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    api_logger.info(f"Delete API request: api_id={api_id}, user_id={current_user.id}")
    api = api_service.get_api_by_id(db=db, api_id=api_id, user=current_user)
    
    if not api:
        api_logger.warning(f"API not found for deletion: api_id={api_id}, user_id={current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API not found"
        )
    
    try:
        api_service.delete_api(db=db, api=api)
        return None
    except Exception as e:
        api_logger.error(f"API deletion failed: api_id={api_id}, user_id={current_user.id}: {str(e)}")
        raise
