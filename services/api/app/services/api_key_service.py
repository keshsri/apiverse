import secrets
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from app.models.api_key import APIKey
from app.models.user import User
from app.utils.logger import api_logger

ph = PasswordHasher()

def generate_api_key(environment: str) -> Tuple[str, str, str]:
    random_part = secrets.token_urlsafe(32)
    full_key = f"apv_{environment}_{random_part}"

    key_hash = ph.hash(full_key)
    key_prefix = full_key[:12] + "...."

    api_logger.info(f"Generated API Key with prefix: {key_prefix}")
    return full_key, key_hash, key_prefix

def create_api_key(
    db: Session,
    user: User,
    name: Optional[str]=None,
    environment: str="live",
    expires_in_days: Optional[int]=None
) -> Tuple[APIKey, str]:
    api_logger.info(f"Creating API key for user: {user.id}, environment: {environment}")

    full_key, key_hash, key_prefix = generate_api_key(environment)
    expires_at = None

    if expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

    api_key = APIKey(
        user_id=user.id,
        key_hash=key_hash,
        key_prefix=key_prefix,
        name=name,
        environment=environment,
        is_active=True,
        expires_at=expires_at
    )

    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    api_logger.info(f"API Key created: id={api_key.id}, prefix={key_prefix}, user_id={user.id}")
    return api_key, full_key

def get_user_api_keys(db: Session, user: User) -> List[APIKey]:
    api_logger.info(f"Fetching API Keys for user_id: {user.id}")

    api_keys = db.query(APIKey).filter(
        APIKey.user_id == user.id
    ).order_by(APIKey.created_at.desc()).all()

    api_logger.info(f"Found {len(api_keys)} API keys for user: {user.id}")
    return api_keys

def verify_api_key(db: Session, api_key: str) -> Optional[APIKey]:
    try:
        key_prefix = api_key[:12] + "...."

        api_key_record = db.query(APIKey).filter(
            APIKey.key_prefix == key_prefix
        ).first()

        if not api_key_record:
            api_logger.warning(f"API Key with prefix: {key_prefix} not found")
            return None

        if not api_key_record.is_active:
            api_logger.warning(f"API key with id: {api_key_record.id} is inactive")
            return None

        if api_key_record.expires_at and api_key_record.expires_at < datetime.utcnow():
            api_logger.warning(f"API Key with id: {api_key_record.id} has expired")
            return None

        try:
            ph.verify(api_key_record.key_hash, api_key)
        except VerifyMismatchError:
            api_logger.warning(f"API Key hash mismatch for id: {api_key_record.id}")
            return None

        api_key_record.last_used_at = datetime.utcnow()
        db.commit()

        api_logger.info(f"API key verified: id: {api_key_record.id}, user: {api_key_record.user_id}")
        return api_key_record
    
    except Exception as e:
        api_logger.error(f"Error verifying API key with error {str(e)}")
        return None

def revoke_api_key(db: Session, api_key_id: int, user: User) -> bool:
    api_logger.info(f"Revoking API Key: id={api_key_id}, user_id={user.id}")

    api_key = db.query(APIKey).filter(
        APIKey.id == api_key_id,
        APIKey.user_id == user.id
    ).first()

    if not api_key:
        api_logger.warning(f"API key not found or access denied: id: {api_key_id}, user: {user.id}")
        return False

    api_key.is_active = False
    db.commit()

    api_logger.info(f"API Key revoked: id: {api_key_id}")
    return True