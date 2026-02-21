import os
import json
import boto3
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

settings = get_settings()

def get_database_url():
    if settings.DATABASE_URL and not settings.DATABASE_URL.startswith("postgresql://placeholder"):
        return settings.DATABASE_URL
    
    if settings.RDS_SECRET_ARN:
        client = boto3.client('secretsmanager')
        response = client.get_secret_value(SecretId=settings.RDS_SECRET_ARN)
        secret = json.loads(response['SecretString'])
        
        username = secret['username']
        password = secret['password']
        
        rds_endpoint = os.environ.get("RDS_ENDPOINT")
        rds_port = os.environ.get("RDS_PORT", "5432")
        database_name = os.environ.get("DATABASE_NAME", "apiverse")
        
        return f"postgresql://{username}:{password}@{rds_endpoint}:{rds_port}/{database_name}"
    
    return settings.DATABASE_URL

database_url = get_database_url()

engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
