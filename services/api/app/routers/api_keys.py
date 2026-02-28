from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.schemas.api_key import (
    APIKeyCreateRequest,
    APIKeyCreateResponse,
    APIKeyResponse,
    APIKeyListResponse
)
from app.services import api_key_service, webhook_service
from app.utils.dependencies import get_current_user
from app.utils.logger import api_logger

router = APIRouter(prefix="/api-keys", tags=["API Keys"])

@router.post("", response_model=APIKeyCreateResponse, status_code=status.HTTP_201_CREATED)
def create_api_key(
    key_data: APIKeyCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    api_logger.info(f"API key creation request for user: {current_user.id}, environment={key_data.environment}")

    try:
        api_key, full_key = api_key_service.create_api_key(
            db=db,
            user=current_user,
            name=key_data.name,
            environment=key_data.environment.value,
            expires_in_days=key_data.expires_in_days
        )

        webhook_service.publish_event(
            event_type='api.key.created',
            api_id=0,
            payload={
                'key_id': api_key.id,
                'key_prefix': api_key.key_prefix,
                'environment': api_key.environment,
                'user_id': current_user.id
            }
        )

        return APIKeyCreateResponse(
            id=api_key.id,
            api_key=full_key,
            key_prefix=api_key.key_prefix,
            name=api_key.name,
            environment=api_key.environment,
            created_at=api_key.created_at,
            expires_at=api_key.expires_at
        )
    
    except Exception as e:
        api_logger.error(f"API key creation failed for user: {current_user.id} with error: {str(e)}")
        raise

@router.get("", response_model=APIKeyListResponse)
def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    api_logger.info(f"Listing API Keys for user: {current_user.id}")

    api_keys = api_key_service.get_user_api_keys(db=db, user=current_user)
    return APIKeyListResponse(total=len(api_keys), api_keys=api_keys)

@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_api_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    api_logger.info(f"Revoke API key request for key: {key_id} by user: {current_user.id}")
    success = api_key_service.revoke_api_key(db=db, api_key_id=key_id, user=current_user)

    if not success:
        api_logger.warning(f"API key not found or access denied: key_id: {key_id} for user: {current_user.id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API Key not found")

    webhook_service.publish_event(
        event_type='api.key.revoked',
        api_id=0,
        payload={
            'key_id': key_id,
            'user_id': current_user.id
        }
    )

    return None