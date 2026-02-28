import redis
import os
from app.utils.logger import api_logger

class RedisService:
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisService, cls).__new__(cls)
        return cls._instance

    def get_client(self) -> redis.Redis:
        if self._client is None:
            redis_host = os.environ.get('REDIS_HOST', 'localhost')
            redis_port = int(os.environ.get('REDIS_PORT', 6379))
            
            self._client = redis.Redis(
                host=redis_host,
                port=redis_port,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            api_logger.info(f"Redis client initialized: {redis_host}:{redis_port}")
        
        return self._client

    def close(self):
        if self._client:
            self._client.close()
            self._client = None

redis_service = RedisService()
