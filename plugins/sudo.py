"""
Sudo plugin - Administrative commands for bot management
Ported from the original sudo.lua
"""

import logging
import os
import asyncio
from utils import UserPermissions, get_chat_id, get_user_id
from config import SUDO_USERS

logger = logging.getLogger(__name__)

async def handle_broadcast(client, event, args, db):
    """Handle /broadcast command - send message to all chats"""
    if not args:
        return "Usage: /broadcast <message>"
    
    admin_id = get_user_id(event.message)
    if not UserPermissions.is_sudo(admin_id):
        return "Only sudo users can broadcast!"
    
    message = " ".join(args)
    sent_count = 0
    failed_count = 0
    
    # Get all chats from database
    try:
        # This is a simplified approach - in reality you'd want to track active chats
        await event.respond("📡 Starting broadcast...")
        
        async for dialog in client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                try:
                    await client.send_message(dialog.id, f"📢 **Broadcast Message**\n\n{message}")
                    sent_count += 1
                    await asyncio.sleep(0.1)  # Rate limiting
                except:
                    failed_count += 1
        
        return f"✅ Broadcast completed!\nSent: {sent_count}\nFailed: {failed_count}"
        
    except Exception as e:
        logger.error(f"Error in broadcast: {e}")
        return "❌ Broadcast failed!"

async def handle_leave(client, event, args, db):
    """Handle /leave command - leave a chat"""
    admin_id = get_user_id(event.message)
    if not UserPermissions.is_sudo(admin_id):
        return "Only sudo users can use this command!"
    
    chat_id = get_chat_id(event.message)
    
    if args and args[0].lstrip('-').isdigit():
        # Leave specific chat by ID
        target_chat_id = int(args[0])
        try:
            await client.send_message(target_chat_id, "👋 Bot is leaving this chat by admin request.")
            await client.delete_dialog(target_chat_id)
            return f"✅ Left chat {target_chat_id}"
        except:
            return f"❌ Failed to leave chat {target_chat_id}"
    else:
        # Leave current chat
        try:
            await event.respond("👋 Bot is leaving this chat by admin request.")
            await client.delete_dialog(chat_id)
            return None
        except:
            return "❌ Failed to leave chat"

async def handle_reload(client, event, args, db):
    """Handle /reload command - reload bot plugins"""
    admin_id = get_user_id(event.message)
    if not UserPermissions.is_sudo(admin_id):
        return "Only sudo users can reload plugins!"
    
    try:
        # This would require reloading the bot - simplified here
        return "🔄 Plugin reload requested (requires bot restart for full effect)"
    except Exception as e:
        logger.error(f"Error reloading: {e}")
        return "❌ Failed to reload plugins"

async def handle_stats(client, event, args, db):
    """Handle /stats command - show bot statistics"""
    admin_id = get_user_id(event.message)
    if not UserPermissions.is_sudo(admin_id):
        return "Only sudo users can view stats!"
    
    try:
        # Get basic stats
        me = await client.get_me()
        
        stats_text = f"**📊 Bot Statistics**\n\n"
        stats_text += f"**Bot:** @{me.username}\n"
        stats_text += f"**Bot ID:** {me.id}\n\n"
        
        # Count dialogs
        group_count = 0
        channel_count = 0
        user_count = 0
        
        async for dialog in client.iter_dialogs(limit=None):
            if dialog.is_group:
                group_count += 1
            elif dialog.is_channel:
                channel_count += 1
            elif dialog.is_user:
                user_count += 1
        
        stats_text += f"**Groups:** {group_count}\n"
        stats_text += f"**Channels:** {channel_count}\n"
        stats_text += f"**Users:** {user_count}\n"
        stats_text += f"**Total Dialogs:** {group_count + channel_count + user_count}\n\n"
        
        # Database stats
        try:
            # Get some Redis stats
            info = db.redis.info()
            stats_text += f"**Database:**\n"
            stats_text += f"Used Memory: {info.get('used_memory_human', 'N/A')}\n"
            stats_text += f"Connected Clients: {info.get('connected_clients', 'N/A')}\n"
            stats_text += f"Commands Processed: {info.get('total_commands_processed', 'N/A')}\n"
        except:
            pass
        
        return stats_text
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return "❌ Failed to get statistics"

async def handle_setlang(client, event, args, db):
    """Handle /setlang command - set bot language"""
    if not args:
        return "Usage: /setlang <en|fa|فا>"
    
    msg = event.message
    admin_id = get_user_id(msg)
    chat_id = get_chat_id(msg)
    
    if not UserPermissions.is_sudo(admin_id):
        return "Only sudo users can set language!"
    
    lang = args[0].lower()
    if lang not in ['en', 'fa', 'فا']:
        return "Supported languages: en, fa, فا"
    
    # Get chat type
    if chat_id != admin_id:  # Not private chat
        chat_entity = await client.get_entity(chat_id)
        if hasattr(chat_entity, 'megagroup') and chat_entity.megagroup:
            chat_type = "sp"  # supergroup
        else:
            chat_type = "gp"  # group
    else:
        return "Please use this command in a group or channel"
    
    db.set_language(chat_type, lang)
    return f"✅ Language set to {lang}"

async def handle_markread(client, event, args, db):
    """Handle /markread command - toggle mark read"""
    admin_id = get_user_id(event.message)
    if not UserPermissions.is_sudo(admin_id):
        return "Only sudo users can toggle mark read!"
    
    current = db.get_bot_setting('markread') or 'off'
    new_value = 'off' if current == 'on' else 'on'
    
    db.set_bot_setting('markread', new_value)
    return f"✅ Mark read {'enabled' if new_value == 'on' else 'disabled'}"

async def handle_support(client, event, args, db):
    """Handle /support command - get support info"""
    support_text = """
🆘 **Bot Support**

**Commands:**
• Use `/help` for user commands
• Use `/settings` to view group settings
• Contact admins for support

**Links:**
• GitHub: https://github.com/your-repo
• Support Group: @your_support_group

**Version:** 2.0 (Telethon)
"""
    return support_text

# Command mappings
COMMANDS = {
    'broadcast': handle_broadcast,
    'leave': handle_leave,
    'reload': handle_reload,
    'stats': handle_stats,
    'setlang': handle_setlang,
    'markread': handle_markread,
    'support': handle_support,
}

PATTERNS = {}

# Plugin metadata
__plugin_name__ = "Sudo"
__plugin_description__ = "Administrative commands for bot management"