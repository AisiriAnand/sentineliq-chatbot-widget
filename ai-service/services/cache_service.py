import hashlib
import json
import redis
import os
from datetime import datetime

class CacheService:
    def __init__(self):
        self.redis_client = None
        self.response_times = []
        self.ttl_seconds = 900  # 15 minutes
        
        try:
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
        except Exception as e:
            print(f"Redis connection failed: {e}")
            self.redis_client = None
    
    def is_connected(self):
        if not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            return False
    
    def _generate_key(self, endpoint, user_input):
        """Generate SHA256 hash key for cache"""
        data = f"{endpoint}:{user_input}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def get(self, endpoint, user_input):
        """Get cached result"""
        if not self.is_connected():
            return None
        
        try:
            key = self._generate_key(endpoint, user_input)
            cached = self.redis_client.get(key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            print(f"Cache get error: {e}")
        
        return None
    
    def set(self, endpoint, user_input, result):
        """Set cache with 15 min TTL"""
        if not self.is_connected():
            return False
        
        try:
            key = self._generate_key(endpoint, user_input)
            self.redis_client.setex(key, self.ttl_seconds, json.dumps(result))
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def record_response_time(self, duration_ms):
        """Record response time for avg calculation"""
        self.response_times.append(duration_ms)
        # Keep last 100 measurements
        if len(self.response_times) > 100:
            self.response_times = self.response_times[-100:]
    
    def get_avg_response_time(self):
        """Get average response time in ms"""
        if not self.response_times:
            return 0
        return sum(self.response_times) / len(self.response_times)
