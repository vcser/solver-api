from functools import wraps
from typing import Callable, Any
import redis
import pickle
from api.config import settings
import logging

logger = logging.getLogger(__name__)

redis_client = redis.Redis.from_url(str(settings.REDIS_URL))

def redis_cache(prefix: str, expire: int = 300):
    def decorator(func: Callable[..., Any]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{prefix}:{str(args[1:])}:{str(kwargs)}"
            
            try:
                # Intentar obtener del caché
                cached = redis_client.get(cache_key)
                if cached:
                    return pickle.loads(cached)
                    
                # Ejecutar función si no está en caché
                result = await func(*args, **kwargs)
                
                # Almacenar en caché
                redis_client.set(cache_key, pickle.dumps(result), ex=expire)
                return result
                
            except redis.RedisError as e:
                logger.warning(f"Cache error: {str(e)}")
                return await func(*args, **kwargs)
                
        return wrapper
    return decorator