import os
import sys
from alembic.config import Config
from alembic import command

def handler(event, context):
    try:
        alembic_cfg = Config("alembic.ini")
        
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            return {
                "statusCode": 500,
                "body": "DATABASE_URL environment variable not set"
            }
        
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
