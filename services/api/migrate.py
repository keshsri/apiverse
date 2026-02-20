import os
import sys
import json
import boto3
from alembic.config import Config
from alembic import command

def get_db_credentials():
    secret_arn = os.environ.get("RDS_SECRET_ARN")
    if not secret_arn:
        raise Exception("RDS_SECRET_ARN environment variable not set")
    
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_arn)
    secret = json.loads(response['SecretString'])
    
    return secret['username'], secret['password']

def handler(event, context):
    try:
        username, password = get_db_credentials()
        
        rds_endpoint = os.environ.get("RDS_ENDPOINT")
        rds_port = os.environ.get("RDS_PORT", "5432")
        database_name = os.environ.get("DATABASE_NAME", "apiverse")
        
        if not rds_endpoint:
            return {
                "statusCode": 500,
                "body": "RDS_ENDPOINT environment variable not set"
            }
        
        database_url = f"postgresql://{username}:{password}@{rds_endpoint}:{rds_port}/{database_name}"
        
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)
        
        command.upgrade(alembic_cfg, "head")
        
        return {
            "statusCode": 200,
            "body": "Migrations completed successfully"
        }
    
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        return {
            "statusCode": 500,
            "body": f"Migration failed: {str(e)}"
        }
