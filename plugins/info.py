"""
Info plugin - Get user and chat information
Ported from the original info.lua
"""

import logging
from telethon.tl.types import User, Chat, Channel
from utils import MessageUtils, get_chat_id, get_user_id
from datetime import datetime

logger = logging.getLogger(__name__)

async def handle_info(client, event, args, db):
    """Handle /info command"""
    msg = event.message
    chat_id = get_chat_id(msg)
    
    # Get target user (from reply or argument)
    if msg.reply_to_msg_id:
        try:
            reply_msg = await client.get_messages(chat_id, ids=msg.reply_to_msg_id)
            target_user = await client.get_entity(reply_msg.sender_id)
        except:
            return "Could not get user info from replied message"
    elif args:
        try:
            if args[0].startswith('@'):
                target_user = await client.get_entity(args[0])
            elif args[0].isdigit():
                target_user = await client.get_entity(int(args[0]))
            else:
                return "Invalid username or ID"
        except:
            return "User not found"
    else:
        # Get info about sender
        target_user = await client.get_entity(msg.sender_id)
    
    if not target_user:
        return "User not found"
    
    # Build info message
    info_text = f"**User Information:**\n\n"
    info_text += f"**Name:** {MessageUtils.user_print_name(target_user)}\n"
    info_text += f"**ID:** `{target_user.id}`\n"
    
    if hasattr(target_user, 'username') and target_user.username:
        info_text += f"**Username:** @{target_user.username}\n"
    
    if hasattr(target_user, 'first_name') and target_user.first_name:
        info_text += f"**First Name:** {target_user.first_name}\n"
    
    if hasattr(target_user, 'last_name') and target_user.last_name:
        info_text += f"**Last Name:** {target_user.last_name}\n"
    
    # Check user status
    if hasattr(target_user, 'bot') and target_user.bot:
        info_text += f"**Type:** Bot\n"
    else:
        info_text += f"**Type:** User\n"
    
    # Check if premium
    if hasattr(target_user, 'premium') and target_user.premium:
        info_text += f"**Premium:** Yes\n"
    
    # Check verification status
    if hasattr(target_user, 'verified') and target_user.verified:
        info_text += f"**Verified:** Yes\n"
    
    # Check restriction status
    if hasattr(target_user, 'restricted') and target_user.restricted:
        info_text += f"**Restricted:** Yes\n"
    
    # Get additional info from database
    user_data = db.get_user(target_user.id)
    if user_data:
        info_text += f"\n**Database Info:**\n"
        if 'print_name' in user_data:
            info_text += f"**Stored Name:** {user_data['print_name']}\n"
    
    # Check global ban status
    if db.is_gbanned(target_user.id):
        info_text += f"\n⚠️ **GLOBALLY BANNED** ⚠️\n"
    
    # Check whitelist status
    if db.is_whitelisted(target_user.id):
        info_text += f"\n✅ **WHITELISTED** ✅\n"
    
    # Check local ban status (if in group)
    if chat_id != target_user.id:  # Not in private chat
        if db.is_banned(target_user.id, chat_id):
            info_text += f"\n🚫 **BANNED IN THIS CHAT** 🚫\n"
    
    # Get message stats
    msg_count = db.get_user_chat_msgs(target_user.id, chat_id)
    if msg_count:
        info_text += f"**Messages in this chat:** {msg_count}\n"
    
    return info_text

async def handle_id(client, event, args, db):
    """Handle /id command"""
    msg = event.message
    chat_id = get_chat_id(msg)
    
    response = f"**IDs:**\n\n"
    
    # Chat ID
    if chat_id != msg.sender_id:  # In a group/channel
        try:
            chat_entity = await client.get_entity(chat_id)
            chat_name = getattr(chat_entity, 'title', 'Unknown')
            response += f"**Chat:** {chat_name}\n"
            response += f"**Chat ID:** `{chat_id}`\n\n"
        except:
            response += f"**Chat ID:** `{chat_id}`\n\n"
    
    # User ID
    if msg.reply_to_msg_id:
        try:
            reply_msg = await client.get_messages(chat_id, ids=msg.reply_to_msg_id)
            target_user = await client.get_entity(reply_msg.sender_id)
            response += f"**User:** {MessageUtils.user_print_name(target_user)}\n"
            response += f"**User ID:** `{target_user.id}`\n"
        except:
            response += f"**Your ID:** `{msg.sender_id}`\n"
    else:
        response += f"**Your ID:** `{msg.sender_id}`\n"
    
    return response

async def handle_chatinfo(client, event, args, db):
    """Handle /chatinfo command"""
    msg = event.message
    chat_id = get_chat_id(msg)
    
    if chat_id == msg.sender_id:  # Private chat
        return "This command can only be used in groups or channels"
    
    try:
        chat_entity = await client.get_entity(chat_id)
        
        info_text = f"**Chat Information:**\n\n"
        
        if hasattr(chat_entity, 'title'):
            info_text += f"**Title:** {chat_entity.title}\n"
        
        info_text += f"**ID:** `{chat_id}`\n"
        
        if hasattr(chat_entity, 'username') and chat_entity.username:
            info_text += f"**Username:** @{chat_entity.username}\n"
        
        # Chat type
        chat_type = MessageUtils.get_chat_type(chat_entity)
        info_text += f"**Type:** {chat_type.title()}\n"
        
        # Member count (for channels/supergroups)
        if isinstance(chat_entity, Channel):
            try:
                full_chat = await client.get_entity(chat_entity)
                if hasattr(full_chat, 'participants_count'):
                    info_text += f"**Members:** {full_chat.participants_count}\n"
            except:
                pass
        
        # Description
        if hasattr(chat_entity, 'about') and chat_entity.about:
            info_text += f"**Description:** {chat_entity.about}\n"
        
        # Creation date
        if hasattr(chat_entity, 'date'):
            creation_date = chat_entity.date.strftime("%Y-%m-%d %H:%M:%S")
            info_text += f"**Created:** {creation_date}\n"
        
        # Settings from database
        settings = db.get_chat_settings(chat_id)
        if settings:
            info_text += f"\n**Bot Settings:**\n"
            for key, value in settings.items():
                info_text += f"**{key.title()}:** {value}\n"
        
        return info_text
        
    except Exception as e:
        logger.error(f"Error getting chat info: {e}")
        return "Failed to get chat information"

# Command mappings
COMMANDS = {
    'info': handle_info,
    'id': handle_id,
    'chatinfo': handle_chatinfo,
}

PATTERNS = {}

# Plugin metadata
__plugin_name__ = "Info"
__plugin_description__ = "Get user and chat information"