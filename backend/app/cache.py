import hashlib
import json
import time
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class MemoryCache:
    """Simple in-memory cache for API responses"""
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
    
    def _generate_key(self, data: Any) -> str:
        """Generate a cache key from data"""
        if isinstance(data, bytes):
            # For image data, use hash
            return hashlib.md5(data).hexdigest()
        else:
            # For other data, serialize and hash
            serialized = json.dumps(data, sort_keys=True, default=str)
            return hashlib.md5(serialized.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        if key in self.cache:
            entry = self.cache[key]
            if time.time() < entry['expires_at']:
                logger.info(f"Cache hit for key: {key[:10]}...")
                return entry['data']
            else:
                # Expired, remove from cache
                del self.cache[key]
                logger.info(f"Cache expired for key: {key[:10]}...")
        return None
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> None:
        """Set item in cache"""
        ttl = ttl or self.default_ttl
        expires_at = time.time() + ttl
        
        self.cache[key] = {
            'data': data,
            'expires_at': expires_at
        }
        logger.info(f"Cached data for key: {key[:10]}... (TTL: {ttl}s)")
    
    def clear(self) -> None:
        """Clear all cached items"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_items = len(self.cache)
        expired_items = sum(1 for entry in self.cache.values() if time.time() >= entry['expires_at'])
        
        return {
            'total_items': total_items,
            'active_items': total_items - expired_items,
            'expired_items': expired_items
        }

# Global cache instance
cache = MemoryCache(default_ttl=600)  # 10 minutes default

def cache_key_from_image(image_data: bytes, additional_params: Dict = None) -> str:
    """Generate cache key for image-based operations"""
    base_key = cache._generate_key(image_data)
    
    if additional_params:
        params_key = cache._generate_key(additional_params)
        return f"{base_key}_{params_key}"
    
    return base_key