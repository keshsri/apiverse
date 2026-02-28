from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.user import User
from app.schemas.webhook import (
    WebhookSubscriptionCreate,
    WebhookSubscriptionUpdate,
    WebhookSubscriptionResponse,
    WebhookDeliveryResponse
)
from app.services import webhook_service
from app.utils.dependencies import get_current_user
from app.utils.logger import api_logger

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

@router.post("/subscriptions", response_model=WebhookSubscriptionResponse, status_code=status.HTTP_201_CREATED)
def create_subscription(
    subscription_data: WebhookSubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    api_logger.info(f"Create webhook subscription for api_id={subscription_data.api_id}, user_id={current_user.id}")
    
    try:
        subscription = webhook_service.create_subscription(
            db=db,
            api_id=subscription_data.api_id,
            user=current_user,
            event_type=subscription_data.event_type,
            callback_url=str(subscription_data.callback_url),
            secret=subscription_data.secret,
            is_active=subscription_data.is_active
        )
        return subscription
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/subscriptions", response_model=List[WebhookSubscriptionResponse])
def list_subscriptions(
    api_id: int = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    api_logger.info(f"List webhook subscriptions for api_id={api_id}, user_id={current_user.id}")
    
    subscriptions = webhook_service.get_subscriptions(
        db=db,
        api_id=api_id,
        user=current_user
    )
    
    return subscriptions

@router.get("/subscriptions/{subscription_id}", response_model=WebhookSubscriptionResponse)
def get_subscription(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    api_logger.info(f"Get webhook subscription: id={subscription_id}, user_id={current_user.id}")
    
    subscription = webhook_service.get_subscription(
        db=db,
        subscription_id=subscription_id,
        user=current_user
    )
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook subscription not found"
        )
    
    return subscription

@router.put("/subscriptions/{subscription_id}", response_model=WebhookSubscriptionResponse)
def update_subscription(
    subscription_id: int,
    subscription_data: WebhookSubscriptionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    api_logger.info(f"Update webhook subscription: id={subscription_id}, user_id={current_user.id}")
    
    subscription = webhook_service.update_subscription(
        db=db,
        subscription_id=subscription_id,
        user=current_user,
        callback_url=str(subscription_data.callback_url) if subscription_data.callback_url else None,
        secret=subscription_data.secret,
        is_active=subscription_data.is_active
    )
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook subscription not found"
        )
    
    return subscription

@router.delete("/subscriptions/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subscription(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    api_logger.info(f"Delete webhook subscription: id={subscription_id}, user_id={current_user.id}")
    
    success = webhook_service.delete_subscription(
        db=db,
        subscription_id=subscription_id,
        user=current_user
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook subscription not found"
        )

@router.get("/subscriptions/{subscription_id}/deliveries", response_model=List[WebhookDeliveryResponse])
def get_deliveries(
    subscription_id: int,
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    api_logger.info(f"Get webhook deliveries for subscription_id={subscription_id}, user_id={current_user.id}")
    
    deliveries = webhook_service.get_deliveries(
        db=db,
        subscription_id=subscription_id,
        user=current_user,
        limit=limit
    )
    
    return deliveries
