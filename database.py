import json
import os
import threading
import time
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class FileDatabase:
    """Simple file-based database using JSON"""
    
    def __init__(self, data_file: str = "data/bot_data.json"):
        self.data_file = Path(data_file)
        self.data_file.parent.mkdir(exist_ok=True)
        self._lock = threading.Lock()
        self.data = self._load_data()
        self._last_save = time.time()
        
    def _load_data(self) -> Dict[str, Any]:
        """Load data from file"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.info(f"Loaded data from {self.data_file}")
                return data
        except Exception as e:
            logger.error(f"Error loading data: {e}")
        
        # Return default structure
        return {
            'users': {},
            'banned': {},
            'gbanned': [],
            'whitelist': [],
            'chat_users': {},
            'user_msgs': {},
            'spam_count': {},
            'chat_settings': {},
            'help_texts': {},
            'languages': {},
            'bot_settings': {},
            'user_chat_msgs': {}
        }
    
    def _save_data(self, force: bool = False):
        """Save data to file (with rate limiting)"""
        current_time = time.time()
        if not force and current_time - self._last_save < 5:  # Save at most every 5 seconds
            return
            
        try:
            with self._lock:
                # Create backup
                if self.data_file.exists():
                    backup_file = self.data_file.with_suffix('.bak')
                    self.data_file.replace(backup_file)
                
                # Write new data
                with open(self.data_file, 'w', encoding='utf-8') as f:
                    json.dump(self.data, f, indent=2, ensure_ascii=False)
                
                self._last_save = current_time
                logger.debug("Data saved successfully")
                
        except Exception as e:
            logger.error(f"Error saving data: {e}")
    
    def save(self):
        """Force save data"""
        self._save_data(force=True)
    
    # User management
    def save_user(self, user_id: int, user_data: Dict[str, Any]):
        """Save user information"""
        with self._lock:
            self.data['users'][str(user_id)] = user_data
        self._save_data()
    
    def get_user(self, user_id: int) -> Dict[str, str]:
        """Get user information"""
        return self.data['users'].get(str(user_id), {})
    
    def is_banned(self, user_id: int, chat_id: int) -> bool:
        """Check if user is banned in specific chat"""
        banned_key = f"{user_id}:{chat_id}"
        return banned_key in self.data['banned']
    
    def ban_user(self, user_id: int, chat_id: int, admin_id: int):
        """Ban user in specific chat"""
        with self._lock:
            banned_key = f"{user_id}:{chat_id}"
            self.data['banned'][banned_key] = admin_id
        self._save_data()
    
    def unban_user(self, user_id: int, chat_id: int):
        """Unban user in specific chat"""
        with self._lock:
            banned_key = f"{user_id}:{chat_id}"
            self.data['banned'].pop(banned_key, None)
        self._save_data()
    
    def is_gbanned(self, user_id: int) -> bool:
        """Check if user is globally banned"""
        return user_id in self.data['gbanned']
    
    def gban_user(self, user_id: int):
        """Globally ban user"""
        with self._lock:
            if user_id not in self.data['gbanned']:
                self.data['gbanned'].append(user_id)
        self._save_data()
    
    def ungban_user(self, user_id: int):
        """Remove global ban"""
        with self._lock:
            if user_id in self.data['gbanned']:
                self.data['gbanned'].remove(user_id)
        self._save_data()
    
    def add_to_whitelist(self, user_id: int):
        """Add user to whitelist"""
        with self._lock:
            if user_id not in self.data['whitelist']:
                self.data['whitelist'].append(user_id)
        self._save_data()
    
    def remove_from_whitelist(self, user_id: int):
        """Remove user from whitelist"""
        with self._lock:
            if user_id in self.data['whitelist']:
                self.data['whitelist'].remove(user_id)
        self._save_data()
    
    def is_whitelisted(self, user_id: int) -> bool:
        """Check if user is whitelisted"""
        return user_id in self.data['whitelist']
    
    def get_whitelist(self) -> List[int]:
        """Get all whitelisted users"""
        return self.data['whitelist'].copy()
    
    def clear_whitelist(self):
        """Clear whitelist"""
        with self._lock:
            self.data['whitelist'].clear()
        self._save_data()
    
    # Anti-spam
    def increment_user_msgs(self, user_id: int) -> int:
        """Increment and return user message count"""
        with self._lock:
            current_time = int(time.time())
            key = f"{user_id}:{current_time // 2}"  # 2-second windows
            
            # Clean old entries (older than 10 seconds)
            to_remove = []
            for msg_key in self.data['user_msgs']:
                if msg_key.startswith(f"{user_id}:"):
                    timestamp = int(msg_key.split(':')[1])
                    if current_time - timestamp * 2 > 10:
                        to_remove.append(msg_key)
            
            for old_key in to_remove:
                self.data['user_msgs'].pop(old_key, None)
            
            # Increment current count
            self.data['user_msgs'][key] = self.data['user_msgs'].get(key, 0) + 1
            
            # Count total messages in current window
            total = sum(count for msg_key, count in self.data['user_msgs'].items() 
                       if msg_key.startswith(f"{user_id}:"))
            
            return total
    
    def increment_spam_count(self, user_id: int) -> int:
        """Increment spam count for global ban tracking"""
        with self._lock:
            self.data['spam_count'][str(user_id)] = self.data['spam_count'].get(str(user_id), 0) + 1
        self._save_data()
        return self.data['spam_count'][str(user_id)]
    
    def reset_spam_count(self, user_id: int):
        """Reset spam count"""
        with self._lock:
            self.data['spam_count'][str(user_id)] = 0
        self._save_data()
    
    def get_spam_count(self, user_id: int) -> int:
        """Get spam count"""
        return self.data['spam_count'].get(str(user_id), 0)
    
    # Chat management
    def add_chat_user(self, chat_id: int, user_id: int):
        """Add user to chat user list"""
        with self._lock:
            chat_key = str(chat_id) if chat_id < 0 else f"PM:{user_id}"
            if chat_key not in self.data['chat_users']:
                self.data['chat_users'][chat_key] = []
            if user_id not in self.data['chat_users'][chat_key]:
                self.data['chat_users'][chat_key].append(user_id)
        self._save_data()
    
    def get_chat_users(self, chat_id: int) -> List[int]:
        """Get all users in chat"""
        chat_key = str(chat_id)
        return self.data['chat_users'].get(chat_key, [])
    
    def increment_user_chat_msgs(self, user_id: int, chat_id: int) -> int:
        """Increment user message count in specific chat"""
        with self._lock:
            key = f"{user_id}:{chat_id}"
            self.data['user_chat_msgs'][key] = self.data['user_chat_msgs'].get(key, 0) + 1
        self._save_data()
        return self.data['user_chat_msgs'][key]
    
    def get_user_chat_msgs(self, user_id: int, chat_id: int) -> int:
        """Get user message count in specific chat"""
        key = f"{user_id}:{chat_id}"
        return self.data['user_chat_msgs'].get(key, 0)
    
    # Settings management
    def set_chat_setting(self, chat_id: int, setting: str, value: str):
        """Set chat setting"""
        with self._lock:
            chat_key = str(chat_id)
            if chat_key not in self.data['chat_settings']:
                self.data['chat_settings'][chat_key] = {}
            self.data['chat_settings'][chat_key][setting] = value
        self._save_data()
    
    def get_chat_setting(self, chat_id: int, setting: str) -> Optional[str]:
        """Get chat setting"""
        chat_key = str(chat_id)
        return self.data['chat_settings'].get(chat_key, {}).get(setting)
    
    def get_chat_settings(self, chat_id: int) -> Dict[str, str]:
        """Get all chat settings"""
        chat_key = str(chat_id)
        return self.data['chat_settings'].get(chat_key, {})
    
    def delete_chat_setting(self, chat_id: int, setting: str):
        """Delete chat setting"""
        with self._lock:
            chat_key = str(chat_id)
            if chat_key in self.data['chat_settings']:
                self.data['chat_settings'][chat_key].pop(setting, None)
        self._save_data()
    
    # Help system
    def set_help_text(self, chat_type: str, text: str, chat_id: Optional[int] = None):
        """Set help text for chat type or specific chat"""
        with self._lock:
            key = f"{chat_id}" if chat_id else chat_type
            self.data['help_texts'][key] = text
        self._save_data()
    
    def get_help_text(self, chat_type: str, chat_id: Optional[int] = None) -> Optional[str]:
        """Get help text for chat type or specific chat"""
        # Try specific chat first, then general type
        if chat_id:
            key = str(chat_id)
            text = self.data['help_texts'].get(key)
            if text:
                return text
        
        return self.data['help_texts'].get(chat_type)
    
    def delete_help_text(self, chat_type: str, chat_id: Optional[int] = None):
        """Delete help text"""
        with self._lock:
            key = str(chat_id) if chat_id else chat_type
            self.data['help_texts'].pop(key, None)
        self._save_data()
    
    # Language settings
    def set_language(self, chat_type: str, language: str):
        """Set language for chat type"""
        with self._lock:
            self.data['languages'][chat_type] = language
        self._save_data()
    
    def get_language(self, chat_type: str) -> Optional[str]:
        """Get language for chat type"""
        return self.data['languages'].get(chat_type)
    
    # Bot settings
    def set_bot_setting(self, setting: str, value: str):
        """Set bot setting"""
        with self._lock:
            self.data['bot_settings'][setting] = value
        self._save_data()
    
    def get_bot_setting(self, setting: str) -> Optional[str]:
        """Get bot setting"""
        return self.data['bot_settings'].get(setting)
    
    # Moderation data (for compatibility)
    def save_moderation_data(self, data: Dict[str, Any]):
        """Save moderation data"""
        with self._lock:
            self.data['moderation'] = data
        self._save_data()
    
    def load_moderation_data(self) -> Dict[str, Any]:
        """Load moderation data"""
        return self.data.get('moderation', {})

# Global database instance
db = FileDatabase()