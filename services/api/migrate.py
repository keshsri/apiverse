import os
import sys
import json
import boto3

def get_db_credentials_and_set_env():
    secret_arn = os.environ.get("RDS_SECRET_ARN")
    if not secret_arn:
        raise Exception("RDS_SECRET_ARN environment variable not set")
    
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_arn)
    secret = json.loads(response['SecretString'])
    
    username = secret['username']
    password = secret['password']
    
    rds_endpoint = os.environ.get("RDS_ENDPOINT")
    rds_port = os.environ.get("RDS_PORT", "5432")
    database_name = os.environ.get("DATABASE_NAME", "apiverse")
    
    if not rds_endpoint:
        raise Exception("RDS_ENDPOINT environment variable not set")
    
    database_url = f"postgresql://{username}:{password}@{rds_endpoint}:{rds_port}/{database_name}"

    os.environ["DATABASE_URL"] = database_url
    
    return database_url

try:
    database_url = get_db_credentials_and_set_env()
except Exception as e:
    print(f"Failed to set DATABASE_URL: {str(e)}")
    database_url = None

from alembic.config import Config
from alembic import command

def handler(event, context):
    """
    Lambda handler for running Alembic migrations.
    Can be invoked manually or from GitHub Actions.
    """
    try:
        if not database_url:
            return {
                "statusCode": 500,
                "body": "Failed to retrieve database credentials"
            }
        
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)

        command.upgrade(alembic_cfg, "head")
        
        return {
            "statusCode": 200,
            "body": "Migrations completed successfully"
        }
    
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "statusCode": 500,
            "body": f"Migration failed: {str(e)}"
        }
