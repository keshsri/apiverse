import json
import hmac
import hashlib
import httpx
import boto3
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.webhook_subscription import WebhookSubscription
from app.models.webhook_delivery import WebhookDelivery
from app.models.api import API
from app.models.user import User
from app.utils.logger import api_logger

eventbridge_client = boto3.client('events')

def create_subscription(
    db: Session,
    api_id: int,
    user: User,
    event_type: str,
    callback_url: str,
    secret: Optional[str] = None,
    is_active: bool = True
) -> WebhookSubscription:
    api = db.query(API).filter(API.id == api_id, API.user_id == user.id).first()
    if not api:
        raise ValueError("API not found or access denied")
    
    subscription = WebhookSubscription(
        api_id=api_id,
        event_type=event_type,
        callback_url=callback_url,
        secret=secret,
        is_active=is_active
    )
    
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    
    api_logger.info(f"Created webhook subscription: id={subscription.id}, api_id={api_id}, event={event_type}")
    return subscription

def get_subscriptions(
    db: Session,
    api_id: int,
    user: User
) -> List[WebhookSubscription]:
    api = db.query(API).filter(API.id == api_id, API.user_id == user.id).first()
    if not api:
        return []
    
    return db.query(WebhookSubscription).filter(
        WebhookSubscription.api_id == api_id
    ).all()

def get_subscription(
    db: Session,
    subscription_id: int,
    user: User
) -> Optional[WebhookSubscription]:
    subscription = db.query(WebhookSubscription).join(API).filter(
        WebhookSubscription.id == subscription_id,
        API.user_id == user.id
    ).first()
    
    return subscription

def update_subscription(
    db: Session,
    subscription_id: int,
    user: User,
    callback_url: Optional[str] = None,
    secret: Optional[str] = None,
    is_active: Optional[bool] = None
) -> Optional[WebhookSubscription]:
    subscription = get_subscription(db, subscription_id, user)
    if not subscription:
        return None
    
    if callback_url is not None:
        subscription.callback_url = callback_url
    if secret is not None:
        subscription.secret = secret
    if is_active is not None:
        subscription.is_active = is_active
    
    db.commit()
    db.refresh(subscription)
    
    api_logger.info(f"Updated webhook subscription: id={subscription_id}")
    return subscription

def delete_subscription(
    db: Session,
    subscription_id: int,
    user: User
) -> bool:
    subscription = get_subscription(db, subscription_id, user)
    if not subscription:
        return False
    
    db.delete(subscription)
    db.commit()
    
    api_logger.info(f"Deleted webhook subscription: id={subscription_id}")
    return True

def publish_event(
    event_type: str,
    api_id: int,
    payload: dict
):
    try:
        event_detail = {
            'event_type': event_type,
            'api_id': api_id,
            'payload': payload,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        response = eventbridge_client.put_events(
            Entries=[
                {
                    'Source': 'apiverse.webhooks',
                    'DetailType': event_type,
                    'Detail': json.dumps(event_detail),
                    'EventBusName': 'apiverse-events'
                }
            ]
        )
        
        api_logger.info(f"Published event to EventBridge: {event_type}, api_id={api_id}")
        return response
    except Exception as e:
        api_logger.error(f"Failed to publish event: {str(e)}")
        return None

def generate_signature(payload: str, secret: str) -> str:
    return hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()

async def deliver_webhook(
    db: Session,
    subscription: WebhookSubscription,
    event_type: str,
    payload: dict
):
    delivery = WebhookDelivery(
        subscription_id=subscription.id,
        event_type=event_type,
        payload=payload,
        status='pending',
        attempt_count=0
    )
    
    db.add(delivery)
    db.commit()
    db.refresh(delivery)
    
    payload_str = json.dumps(payload)
    headers = {
        'Content-Type': 'application/json',
        'X-Webhook-Event': event_type,
        'X-Webhook-Delivery': str(delivery.id)
    }
    
    if subscription.secret:
        signature = generate_signature(payload_str, subscription.secret)
        headers['X-Webhook-Signature'] = f'sha256={signature}'
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                subscription.callback_url,
                content=payload_str,
                headers=headers
            )
        
        delivery.status = 'delivered' if response.status_code < 400 else 'failed'
        delivery.response_code = response.status_code
        delivery.response_body = response.text[:1000]
        delivery.delivered_at = datetime.utcnow()
        delivery.attempt_count = 1
        
        api_logger.info(f"Webhook delivered: id={delivery.id}, status={delivery.status}")
        
    except Exception as e:
        delivery.status = 'failed'
        delivery.response_body = str(e)[:1000]
        delivery.attempt_count = 1
        
        api_logger.error(f"Webhook delivery failed: id={delivery.id}, error={str(e)}")
    
    db.commit()
    db.refresh(delivery)
    return delivery

def get_deliveries(
    db: Session,
    subscription_id: int,
    user: User,
    limit: int = 50
) -> List[WebhookDelivery]:
    subscription = get_subscription(db, subscription_id, user)
    if not subscription:
        return []
    
    return db.query(WebhookDelivery).filter(
        WebhookDelivery.subscription_id == subscription_id
    ).order_by(
        WebhookDelivery.created_at.desc()
    ).limit(limit).all()
