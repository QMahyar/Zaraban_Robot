"""
Help system plugin - Manages help text and language settings
Ported from the original help.lua
"""

import logging
import os
from utils import UserPermissions, MessageUtils, get_chat_id, get_user_id
from config import DEFAULT_HELP_TEXT, TEMP_DIR

logger = logging.getLogger(__name__)

async def handle_help(client, event, args, db):
    """Handle /help command"""
    msg = event.message
    chat_id = get_chat_id(msg)
    user_id = get_user_id(msg)
    
    # Get chat type
    chat_entity = await client.get_entity(chat_id)
    chat_type = MessageUtils.get_chat_type(chat_entity)
    
    # Check if user can see help
    if chat_type != "user":
        # Check if user is moderator
        is_mod = await UserPermissions.is_admin(client, chat_id, user_id) or UserPermissions.is_sudo(user_id)
        if not is_mod:
            return "You can't see /help text"
    
    # Get help text
    help_text = get_help_text(db, chat_type, chat_id)
    
    if help_text:
        # Add footer if custom help exists
        try:
            team_file = open("./system/team", "r")
            channel_file = open("./system/channel", "r")
            team = team_file.read().strip()
            channel = channel_file.read().strip()
            team_file.close()
            channel_file.close()
            
            if db.get_help_text(chat_type, chat_id):  # Custom help exists
                help_text += f"\n\n⚡️ [👉 Powered by {team} ] ⚡️\n📎 [👉 Join: {channel} ]"
        except:
            pass
        
        return help_text
    else:
        return "Error! Help text not found! Please use /sethelp (text) or /setlang [en/fa/فا] to fix it."

async def handle_sethelp(client, event, args, db):
    """Handle /sethelp command"""
    if not args:
        return "Usage: /sethelp <help text>"
    
    msg = event.message
    chat_id = get_chat_id(msg)
    user_id = get_user_id(msg)
    help_text = " ".join(args)
    
    # Get chat type
    chat_entity = await client.get_entity(chat_id)
    chat_type = MessageUtils.get_chat_type(chat_entity)
    
    if UserPermissions.is_sudo(user_id):
        # Sudo can set global help
        if chat_type == "channel":
            db.set_help_text("sp", help_text)
            save_help_file("HelpSuper.txt", help_text)
            return "Help of supergroup has been changed successful!"
        elif chat_type == "chat":
            db.set_help_text("gp", help_text)
            save_help_file("HelpChat.txt", help_text)
            return "Help of chat has been changed successful!"
        elif chat_type == "user":
            return "Please use /sethelp commands in chat or supergroup!"
            
    elif await UserPermissions.is_owner(client, chat_id, user_id):
        # Owner can set group-specific help
        if chat_type in ["chat", "channel"]:
            db.set_help_text("custom", help_text, chat_id)
            save_help_file("HelpOwner.txt", help_text)
            return "Help of your group has been changed successful!"
        else:
            return "Please use /sethelp commands in your chat or supergroup! (If you are an owner.)"
    else:
        return "Just for sudo or owner!"

async def handle_delhelp(client, event, args, db):
    """Handle /delhelp command"""
    msg = event.message
    chat_id = get_chat_id(msg)
    user_id = get_user_id(msg)
    
    # Get chat type
    chat_entity = await client.get_entity(chat_id)
    chat_type = MessageUtils.get_chat_type(chat_entity)
    
    if UserPermissions.is_sudo(user_id):
        # Sudo can delete global help
        if chat_type == "channel":
            if db.get_help_text("sp"):
                db.delete_help_text("sp")
                return "Help of supergroup has been removed!"
            else:
                return "Error! Help not found, please set help text with /sethelp commands."
        elif chat_type == "chat":
            if db.get_help_text("gp"):
                db.delete_help_text("gp")
                return "Help of chat has been removed!"
            else:
                return "Error! Help not found, please set help text with /sethelp commands."
                
    elif await UserPermissions.is_owner(client, chat_id, user_id):
        # Owner can delete group-specific help
        if chat_type in ["chat", "channel"]:
            if db.get_help_text("custom", chat_id):
                db.delete_help_text("custom", chat_id)
                return f"Help of your {chat_type} has been removed!"
            else:
                return "Error! Help not found, please set help text with /sethelp commands."
    else:
        return "You can't remove help text! (Just for sudo)"

def get_help_text(db, chat_type, chat_id):
    """Get appropriate help text"""
    # Try custom help first
    custom_help = db.get_help_text("custom", chat_id)
    if custom_help:
        return custom_help
    
    # Try type-specific help
    if chat_type == "channel":
        type_help = db.get_help_text("sp")
    elif chat_type == "chat":
        type_help = db.get_help_text("gp")
    else:
        type_help = None
    
    if type_help:
        return type_help
    
    # Fall back to language-based default help
    if chat_type == "channel":
        lang = db.get_language("sp")
    elif chat_type == "chat":
        lang = db.get_language("gp")
    else:
        lang = "en"
    
    if lang in DEFAULT_HELP_TEXT:
        return DEFAULT_HELP_TEXT[lang]
    
    return DEFAULT_HELP_TEXT["en"]

def save_help_file(filename, content):
    """Save help text to file for compatibility"""
    try:
        filepath = os.path.join(TEMP_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        logger.error(f"Error saving help file {filename}: {e}")

# Command mappings
COMMANDS = {
    'help': handle_help,
    'sethelp': handle_sethelp,
    'delhelp': handle_delhelp,
}

PATTERNS = {}

# Plugin metadata
__plugin_name__ = "Help System"
__plugin_description__ = "Manages help text and provides user assistance"