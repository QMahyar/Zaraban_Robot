"""
Anti-spam plugin - Prevents flooding and automatically bans spammers
Ported from the original anti_spam.lua
"""

import asyncio
import logging
from telethon.errors import UserAdminInvalidError, ChatAdminRequiredError
from utils import UserPermissions, AntiSpam, ChatLogger, MessageUtils, get_chat_id, get_user_id
from config import FLOOD_LIMIT, FLOOD_TIME_LIMIT, GBAN_LIMIT

logger = logging.getLogger(__name__)

# Track kicked users to prevent multiple kicks
kick_table = set()

async def pre_process(client, msg, db):
    """Pre-process messages for anti-spam detection"""
    global kick_table
    
    # Skip service messages
    if msg.action:
        return True
    
    # Skip own messages
    me = await client.get_me()
    if msg.sender_id == me.id:
        return True
    
    user_id = get_user_id(msg)
    chat_id = get_chat_id(msg)
    
    if not user_id or not chat_id:
        return True
    
    # Skip if user should be ignored
    if AntiSpam.should_ignore_user(user_id):
        return True
    
    # Check if user is admin/mod
    if await UserPermissions.is_admin(client, chat_id, user_id):
        return True
    
    # Check chat flood settings
    flood_setting = db.get_chat_setting(chat_id, 'flood')
    if flood_setting == 'no':
        return True
    
    # Check flood
    if AntiSpam.check_flood(user_id, chat_id, FLOOD_LIMIT):
        await handle_flood(client, msg, db)
        return False  # Block message
    
    return True

async def handle_flood(client, msg, db):
    """Handle flooding user"""
    global kick_table
    
    user_id = get_user_id(msg)
    chat_id = get_chat_id(msg)
    
    # Prevent multiple kicks
    if user_id in kick_table:
        return
    
    kick_table.add(user_id)
    
    try:
        # Delete the message
        await msg.delete()
        
        # For private chats, just block
        if chat_id == user_id:  # Private chat
            spam_count = db.get_spam_count(user_id)
            if spam_count >= 7:
                await client.send_message(user_id, f"User [{user_id}] blocked for spam.")
                # Note: Telethon bots can't block users, only users can block
            return
        
        # Kick user from group/channel
        try:
            await client.kick_participant(chat_id, user_id)
        except (UserAdminInvalidError, ChatAdminRequiredError):
            logger.warning(f"No permission to kick user {user_id} in chat {chat_id}")
            return
        
        # Get user info for notification
        try:
            user = await client.get_entity(user_id)
            user_name = MessageUtils.user_print_name(user)
            username = f"@{user.username}" if user.username else "---"
        except:
            user_name = str(user_id)
            username = "---"
        
        # Send kick notification
        kick_msg = f"User: {user_name}\n"
        if username != "---":
            kick_msg += f"Username: {username}\n"
        else:
            kick_msg += f"ID: {user_id}\n"
        kick_msg += "Status: Kicked by bot for flooding\n\n"
        
        try:
            chat_entity = await client.get_entity(chat_id)
            kick_msg += f"From: {chat_entity.title}"
        except:
            kick_msg += f"From: Chat {chat_id}"
        
        await client.send_message(chat_id, kick_msg)
        
        # Increment global spam count
        spam_count = db.increment_spam_count(user_id)
        
        # Check for global ban
        if spam_count >= GBAN_LIMIT and not UserPermissions.is_sudo(user_id):
            # Global ban the user
            db.gban_user(user_id)
            db.reset_spam_count(user_id)
            
            # Notify about global ban
            gban_msg = f"User [ {user_name} ] {user_id} globally banned (spamming)"
            await client.send_message(chat_id, gban_msg)
            
            # Log to all log groups
            moderation_data = db.load_moderation_data()
            gban_log = moderation_data.get('GBan_log', {})
            
            log_msg = f"User [ {user_name} ] ( {username} ) {user_id} Globally banned from ( {chat_entity.title if 'chat_entity' in locals() else 'Unknown'} ) [ {chat_id} ] (spamming)"
            
            for log_group in gban_log.values():
                try:
                    await client.send_message(int(log_group), log_msg)
                except:
                    pass
        
        # Log the action
        ChatLogger.log_action(chat_id, f"User {user_id} kicked for flooding")
        
    except Exception as e:
        logger.error(f"Error handling flood: {e}")
    
    finally:
        # Remove from kick table after a delay
        asyncio.create_task(remove_from_kick_table(user_id))

async def remove_from_kick_table(user_id):
    """Remove user from kick table after delay"""
    global kick_table
    await asyncio.sleep(5)  # 5 second delay
    kick_table.discard(user_id)

async def cron(client, db):
    """Cron task to clean up kick table"""
    global kick_table
    kick_table.clear()

# Export for plugin system
PATTERNS = {}
COMMANDS = {}

# Plugin metadata
__plugin_name__ = "Anti-Spam"
__plugin_description__ = "Prevents flooding and automatically handles spammers"