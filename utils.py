import logging
import asyncio
import os
from datetime import datetime
from typing import Optional, Union, List
from telethon import types
from telethon.tl.types import User, Chat, Channel
from database import db
from config import SUDO_USERS, LOGS_DIR

logger = logging.getLogger(__name__)

class UserPermissions:
    """Handle user permission checking"""
    
    @staticmethod
    def is_sudo(user_id: int) -> bool:
        """Check if user is sudo"""
        return user_id in SUDO_USERS

    @staticmethod
    async def is_admin(client, chat_id: int, user_id: int) -> bool:
        """Check if user is admin in chat"""
        try:
            participant = await client.get_permissions(chat_id, user_id)
            return participant.is_admin or participant.is_creator
        except:
            return False

    @staticmethod
    async def is_owner(client, chat_id: int, user_id: int) -> bool:
        """Check if user is owner of chat"""
        try:
            participant = await client.get_permissions(chat_id, user_id)
            return participant.is_creator
        except:
            return False

    @staticmethod
    def is_momod(client, msg) -> bool:
        """Check if user is moderator, admin, owner or sudo"""
        user_id = msg.sender_id
        chat_id = msg.peer_id.channel_id if hasattr(msg.peer_id, 'channel_id') else msg.peer_id.chat_id if hasattr(msg.peer_id, 'chat_id') else None
        
        if UserPermissions.is_sudo(user_id):
            return True
            
        if chat_id:
            return asyncio.create_task(UserPermissions.is_admin(client, chat_id, user_id))
        
        return False

class MessageUtils:
    """Utilities for message handling"""
    
    @staticmethod
    def get_chat_type(entity) -> str:
        """Get chat type from entity"""
        if isinstance(entity, User):
            return "user"
        elif isinstance(entity, Chat):
            return "chat"
        elif isinstance(entity, Channel):
            if entity.megagroup:
                return "channel"  # supergroup
            else:
                return "channel"  # channel
        return "unknown"

    @staticmethod
    def get_receiver(msg) -> str:
        """Get receiver string for compatibility"""
        if hasattr(msg.peer_id, 'user_id'):
            return f"user#id{msg.peer_id.user_id}"
        elif hasattr(msg.peer_id, 'chat_id'):
            return f"chat#id{msg.peer_id.chat_id}"
        elif hasattr(msg.peer_id, 'channel_id'):
            return f"channel#id{msg.peer_id.channel_id}"
        return ""

    @staticmethod
    def user_print_name(user) -> str:
        """Get user display name"""
        if hasattr(user, 'first_name') and user.first_name:
            name = user.first_name
            if hasattr(user, 'last_name') and user.last_name:
                name += f" {user.last_name}"
            return name
        elif hasattr(user, 'username') and user.username:
            return f"@{user.username}"
        else:
            return f"User {user.id}"

    @staticmethod
    async def get_user_from_message(client, msg, arg: str = None):
        """Get user entity from message (reply or mention)"""
        user = None
        
        # If replying to a message
        if msg.reply_to_msg_id:
            reply_msg = await client.get_messages(msg.peer_id, ids=msg.reply_to_msg_id)
            if reply_msg:
                user = await client.get_entity(reply_msg.sender_id)
        
        # If username/ID provided as argument
        elif arg:
            try:
                if arg.startswith('@'):
                    user = await client.get_entity(arg)
                elif arg.isdigit():
                    user = await client.get_entity(int(arg))
                else:
                    # Try to find user by name
                    async for dialog in client.iter_dialogs():
                        if hasattr(dialog.entity, 'first_name') and dialog.entity.first_name:
                            if arg.lower() in dialog.entity.first_name.lower():
                                user = dialog.entity
                                break
            except:
                pass
        
        return user

class ChatLogger:
    """Handle chat logging"""
    
    @staticmethod
    def log_action(chat_id: int, action: str):
        """Log action to file"""
        try:
            log_file = os.path.join(LOGS_DIR, f"{chat_id}_log.txt")
            timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
            
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"{timestamp} => {action}\n\n")
        except Exception as e:
            logger.error(f"Failed to log action: {e}")

class AntiSpam:
    """Anti-spam utilities"""
    
    @staticmethod
    def should_ignore_user(user_id: int) -> bool:
        """Check if user should be ignored by anti-spam"""
        return (UserPermissions.is_sudo(user_id) or 
                db.is_whitelisted(user_id))

    @staticmethod
    def check_flood(user_id: int, chat_id: int, flood_limit: int = 5) -> bool:
        """Check if user is flooding"""
        count = db.increment_user_msgs(user_id)
        
        # Get chat-specific flood limit
        chat_flood_limit = db.get_chat_setting(chat_id, 'flood_msg_max')
        if chat_flood_limit:
            try:
                flood_limit = int(chat_flood_limit)
            except:
                pass
                
        return count > flood_limit

    @staticmethod
    def check_gban_threshold(user_id: int, gban_limit: int = 4) -> bool:
        """Check if user should be globally banned"""
        spam_count = db.increment_spam_count(user_id)
        return spam_count >= gban_limit

class TextUtils:
    """Text processing utilities"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean text from RTL and special characters"""
        if not text:
            return ""
        # Remove RTL override character
        text = text.replace("‮", "")
        # Remove underscores for logging
        text = text.replace("_", "")
        return text.strip()

    @staticmethod
    def escape_markdown(text: str) -> str:
        """Escape markdown special characters"""
        escape_chars = ['*', '_', '`', '[', ']', '(', ')', '~', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in escape_chars:
            text = text.replace(char, f'\\{char}')
        return text

def get_chat_id(msg) -> Optional[int]:
    """Extract chat ID from message"""
    if hasattr(msg.peer_id, 'channel_id'):
        return msg.peer_id.channel_id
    elif hasattr(msg.peer_id, 'chat_id'):
        return msg.peer_id.chat_id
    elif hasattr(msg.peer_id, 'user_id'):
        return msg.peer_id.user_id
    return None

def get_user_id(msg) -> Optional[int]:
    """Extract user ID from message"""
    return msg.sender_id if hasattr(msg, 'sender_id') else None