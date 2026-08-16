import json
import hashlib
import logging
from redis.asyncio import Redis
from helper import get_settings

logger = logging.getLogger(__name__)


class RedisCacheController:

    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client   
        self.app_settings = get_settings()
        self.default_ttl = self.app_settings.CACHE_TTL_SECONDS

    @staticmethod
    def build_search_cache_key(error_id: str, pagesize: int, min_similarity: float, limit: int) -> str:
        params_signature = json.dumps(
            {"pagesize": pagesize, "min_similarity": min_similarity, "limit": limit},
            sort_keys=True    
        )
        combined = f"search:{error_id}:{params_signature}"
        return hashlib.sha256(combined.encode()).hexdigest()

    async def get(self, key: str):
        try:
            raw = await self.redis_client.get(key)
        except Exception:
            logger.exception("RedisCacheController.get failed for key %s", key)
            return None          
        if raw is None:
            return None           

        try:
            return json.loads(raw)   
        except (json.JSONDecodeError, TypeError):
            logger.exception("RedisCacheController.get: invalid JSON for key %s", key)
            return None


    async def set(self, key: str, value, ttl: int = None):
        try:
            await self.redis_client.set(
                key,
                json.dumps(value),         
                ex=ttl or self.default_ttl  
            )
            return True
        except Exception:
            logger.exception("RedisCacheController.set failed for key %s", key)
            return False

    