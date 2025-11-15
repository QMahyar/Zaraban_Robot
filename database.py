import redis
import json
import logging
from typing import Dict, Any, List, Optional
from config import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        try:
            self.redis = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                password=REDIS_PASSWORD,
                decode_responses=True
            )
            # Test connection
            self.redis.ping()
            logger.info("Connected to Redis database")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    # User management
    def save_user(self, user_id: int, user_data: Dict[str, Any]):
        """Save user information"""
        key = f"user:{user_id}"
        self.redis.hset(key, mapping=user_data)

    def get_user(self, user_id: int) -> Dict[str, str]:
        """Get user information"""
        key = f"user:{user_id}"
        return self.redis.hgetall(key)

    def is_banned(self, user_id: int, chat_id: int) -> bool:
        """Check if user is banned in specific chat"""
        key = f"banned:{user_id}:{chat_id}"
        return self.redis.exists(key) > 0

    def ban_user(self, user_id: int, chat_id: int, admin_id: int):
        """Ban user in specific chat"""
        key = f"banned:{user_id}:{chat_id}"
        self.redis.set(key, admin_id)

    def unban_user(self, user_id: int, chat_id: int):
        """Unban user in specific chat"""
        key = f"banned:{user_id}:{chat_id}"
        self.redis.delete(key)

    def is_gbanned(self, user_id: int) -> bool:
        """Check if user is globally banned"""
        key = "gbanned"
        return self.redis.sismember(key, user_id)

    def gban_user(self, user_id: int):
        """Globally ban user"""
        key = "gbanned"
        self.redis.sadd(key, user_id)

    def ungban_user(self, user_id: int):
        """Remove global ban"""
        key = "gbanned"
        self.redis.srem(key, user_id)

    def add_to_whitelist(self, user_id: int):
        """Add user to whitelist"""
        key = "whitelist"
        self.redis.sadd(key, user_id)

    def remove_from_whitelist(self, user_id: int):
        """Remove user from whitelist"""
        key = "whitelist"
        self.redis.srem(key, user_id)

    def is_whitelisted(self, user_id: int) -> bool:
        """Check if user is whitelisted"""
        key = "whitelist"
        return self.redis.sismember(key, user_id)

    # Anti-spam
    def increment_user_msgs(self, user_id: int) -> int:
        """Increment and return user message count"""
        key = f"user:{user_id}:msgs"
        count = self.redis.incr(key)
        self.redis.expire(key, 2)  # 2 seconds expiry
        return count

    def increment_spam_count(self, user_id: int) -> int:
        """Increment spam count for global ban tracking"""
        key = f"gban:spam:{user_id}"
        return self.redis.incr(key)

    def reset_spam_count(self, user_id: int):
        """Reset spam count"""
        key = f"gban:spam:{user_id}"
        self.redis.set(key, 0)

    def get_spam_count(self, user_id: int) -> int:
        """Get spam count"""
        key = f"gban:spam:{user_id}"
        count = self.redis.get(key)
        return int(count) if count else 0

    # Chat management
    def add_chat_user(self, chat_id: int, user_id: int):
        """Add user to chat user list"""
        if chat_id < 0:  # Group/supergroup
            key = f"chat:{chat_id}:users"
        else:  # Private chat
            key = f"PM:{user_id}"
        self.redis.sadd(key, user_id)

    def get_chat_users(self, chat_id: int) -> List[str]:
        """Get all users in chat"""
        key = f"chat:{chat_id}:users"
        return list(self.redis.smembers(key))

    def increment_user_chat_msgs(self, user_id: int, chat_id: int) -> int:
        """Increment user message count in specific chat"""
        key = f"msgs:{user_id}:{chat_id}"
        return self.redis.incr(key)

    def get_user_chat_msgs(self, user_id: int, chat_id: int) -> int:
        """Get user message count in specific chat"""
        key = f"msgs:{user_id}:{chat_id}"
        count = self.redis.get(key)
        return int(count) if count else 0

    # Settings management
    def set_chat_setting(self, chat_id: int, setting: str, value: str):
        """Set chat setting"""
        key = f"chat:{chat_id}:settings"
        self.redis.hset(key, setting, value)

    def get_chat_setting(self, chat_id: int, setting: str) -> Optional[str]:
        """Get chat setting"""
        key = f"chat:{chat_id}:settings"
        return self.redis.hget(key, setting)

    def get_chat_settings(self, chat_id: int) -> Dict[str, str]:
        """Get all chat settings"""
        key = f"chat:{chat_id}:settings"
        return self.redis.hgetall(key)

    def delete_chat_setting(self, chat_id: int, setting: str):
        """Delete chat setting"""
        key = f"chat:{chat_id}:settings"
        self.redis.hdel(key, setting)

    # Help system
    def set_help_text(self, chat_type: str, text: str, chat_id: Optional[int] = None):
        """Set help text for chat type or specific chat"""
        if chat_id:
            key = f"help:{chat_id}"
        else:
            key = f"help:{chat_type}"
        self.redis.set(key, text)

    def get_help_text(self, chat_type: str, chat_id: Optional[int] = None) -> Optional[str]:
        """Get help text for chat type or specific chat"""
        # Try specific chat first, then general type
        if chat_id:
            key = f"help:{chat_id}"
            text = self.redis.get(key)
            if text:
                return text
        
        key = f"help:{chat_type}"
        return self.redis.get(key)

    def delete_help_text(self, chat_type: str, chat_id: Optional[int] = None):
        """Delete help text"""
        if chat_id:
            key = f"help:{chat_id}"
        else:
            key = f"help:{chat_type}"
        self.redis.delete(key)

    # Language settings
    def set_language(self, chat_type: str, language: str):
        """Set language for chat type"""
        key = f"{chat_type}:lang"
        self.redis.set(key, language)

    def get_language(self, chat_type: str) -> Optional[str]:
        """Get language for chat type"""
        key = f"{chat_type}:lang"
        return self.redis.get(key)

    # Bot settings
    def set_bot_setting(self, setting: str, value: str):
        """Set bot setting"""
        key = f"bot:{setting}"
        self.redis.set(key, value)

    def get_bot_setting(self, setting: str) -> Optional[str]:
        """Get bot setting"""
        key = f"bot:{setting}"
        return self.redis.get(key)

    # Moderation data (for compatibility with original bot)
    def save_moderation_data(self, data: Dict[str, Any]):
        """Save moderation data as JSON"""
        self.redis.set("moderation:data", json.dumps(data))

    def load_moderation_data(self) -> Dict[str, Any]:
        """Load moderation data from JSON"""
        data = self.redis.get("moderation:data")
        return json.loads(data) if data else {}

# Global database instance
db = Database()