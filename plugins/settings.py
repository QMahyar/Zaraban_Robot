"""
Settings plugin - Manage group settings and locks
Ported from the original supergroup.lua
"""

import logging
from utils import UserPermissions, get_chat_id, get_user_id
from telethon.tl.types import ChatBannedRights

logger = logging.getLogger(__name__)

# Default settings for new groups
DEFAULT_SETTINGS = {
    'flood': 'yes',
    'flood_msg_max': '5',
    'lock_arabic': 'no',
    'lock_member': 'no',
    'lock_rtl': 'no',
    'lock_tgservice': 'no',
    'lock_forward': 'no',
    'lock_reply': 'no',
    'lock_audio': 'no',
    'lock_bot': 'no',
    'lock_contact': 'no',
    'lock_document': 'no',
    'lock_english': 'no',
    'lock_fwd': 'no',
    'lock_game': 'no',
    'lock_gif': 'no',
    'lock_inline': 'no',
    'lock_keyboard': 'no',
    'lock_link': 'no',
    'lock_location': 'no',
    'lock_markdown': 'no',
    'lock_media': 'no',
    'lock_photo': 'no',
    'lock_sticker': 'no',
    'lock_tag': 'no',
    'lock_text': 'no',
    'lock_username': 'no',
    'lock_video': 'no',
    'lock_voice': 'no',
    'public_member': 'no',
}

async def handle_lock(client, event, args, db):
    """Handle /lock command"""
    if not args:
        return get_lock_help()
    
    msg = event.message
    chat_id = get_chat_id(msg)
    admin_id = get_user_id(msg)
    
    # Check if user is admin
    if not await UserPermissions.is_admin(client, chat_id, admin_id) and not UserPermissions.is_sudo(admin_id):
        return "You don't have permission to change settings!"
    
    lock_type = args[0].lower()
    valid_locks = [
        'arabic', 'member', 'rtl', 'tgservice', 'forward', 'reply',
        'audio', 'bot', 'contact', 'document', 'english', 'fwd',
        'game', 'gif', 'inline', 'keyboard', 'link', 'location',
        'markdown', 'media', 'photo', 'sticker', 'tag', 'text',
        'username', 'video', 'voice', 'flood'
    ]
    
    if lock_type not in valid_locks:
        return f"Invalid lock type. Valid types: {', '.join(valid_locks)}"
    
    # Set the lock
    db.set_chat_setting(chat_id, f'lock_{lock_type}', 'yes')
    
    return f"🔒 {lock_type.title()} has been locked!"

async def handle_unlock(client, event, args, db):
    """Handle /unlock command"""
    if not args:
        return get_lock_help()
    
    msg = event.message
    chat_id = get_chat_id(msg)
    admin_id = get_user_id(msg)
    
    # Check if user is admin
    if not await UserPermissions.is_admin(client, chat_id, admin_id) and not UserPermissions.is_sudo(admin_id):
        return "You don't have permission to change settings!"
    
    lock_type = args[0].lower()
    
    # Set the unlock
    db.set_chat_setting(chat_id, f'lock_{lock_type}', 'no')
    
    return f"🔓 {lock_type.title()} has been unlocked!"

async def handle_settings(client, event, args, db):
    """Handle /settings command"""
    msg = event.message
    chat_id = get_chat_id(msg)
    admin_id = get_user_id(msg)
    
    # Check if user is admin or sudo
    if not await UserPermissions.is_admin(client, chat_id, admin_id) and not UserPermissions.is_sudo(admin_id):
        return "You don't have permission to view settings!"
    
    # Get current settings
    settings = db.get_chat_settings(chat_id)
    
    # If no settings exist, initialize with defaults
    if not settings:
        for key, value in DEFAULT_SETTINGS.items():
            db.set_chat_setting(chat_id, key, value)
        settings = DEFAULT_SETTINGS
    
    # Build settings display
    settings_text = "**⚙️ Group Settings:**\n\n"
    
    # Flood settings
    flood_status = settings.get('flood', 'yes')
    flood_limit = settings.get('flood_msg_max', '5')
    settings_text += f"**Flood Protection:** {'✅ Enabled' if flood_status == 'yes' else '❌ Disabled'}\n"
    if flood_status == 'yes':
        settings_text += f"**Flood Limit:** {flood_limit} messages\n"
    settings_text += "\n"
    
    # Lock settings
    settings_text += "**🔒 Locks:**\n"
    lock_categories = {
        'Content': ['text', 'media', 'photo', 'video', 'audio', 'voice', 'document', 'sticker', 'gif'],
        'Features': ['forward', 'reply', 'inline', 'keyboard', 'bot', 'contact', 'location', 'game'],
        'Text': ['arabic', 'english', 'rtl', 'link', 'username', 'tag', 'markdown'],
        'Other': ['member', 'tgservice']
    }
    
    for category, locks in lock_categories.items():
        category_locks = []
        for lock in locks:
            status = settings.get(f'lock_{lock}', 'no')
            if status == 'yes':
                category_locks.append(f"🔒 {lock}")
            else:
                category_locks.append(f"🔓 {lock}")
        
        if category_locks:
            settings_text += f"\n**{category}:**\n"
            settings_text += "\n".join(category_locks) + "\n"
    
    # Other settings
    public_member = settings.get('public_member', 'no')
    settings_text += f"\n**Public Member List:** {'✅ Enabled' if public_member == 'yes' else '❌ Disabled'}\n"
    
    return settings_text

async def handle_setflood(client, event, args, db):
    """Handle /setflood command"""
    if not args:
        return "Usage: /setflood <number>\nExample: /setflood 5"
    
    msg = event.message
    chat_id = get_chat_id(msg)
    admin_id = get_user_id(msg)
    
    # Check if user is admin
    if not await UserPermissions.is_admin(client, chat_id, admin_id) and not UserPermissions.is_sudo(admin_id):
        return "You don't have permission to change flood settings!"
    
    try:
        flood_limit = int(args[0])
        if flood_limit < 1 or flood_limit > 20:
            return "Flood limit must be between 1 and 20"
        
        db.set_chat_setting(chat_id, 'flood_msg_max', str(flood_limit))
        db.set_chat_setting(chat_id, 'flood', 'yes')  # Enable flood protection
        
        return f"✅ Flood limit set to {flood_limit} messages"
        
    except ValueError:
        return "Please provide a valid number"

async def handle_public_member(client, event, args, db):
    """Handle /public member command"""
    msg = event.message
    chat_id = get_chat_id(msg)
    admin_id = get_user_id(msg)
    
    # Check if user is admin
    if not await UserPermissions.is_admin(client, chat_id, admin_id) and not UserPermissions.is_sudo(admin_id):
        return "You don't have permission to change this setting!"
    
    current = db.get_chat_setting(chat_id, 'public_member') or 'no'
    new_value = 'no' if current == 'yes' else 'yes'
    
    db.set_chat_setting(chat_id, 'public_member', new_value)
    
    status = 'enabled' if new_value == 'yes' else 'disabled'
    return f"✅ Public member list {status}!"

def get_lock_help():
    """Get help text for lock commands"""
    return """**🔒 Lock/Unlock Help:**

**Usage:** `/lock <type>` or `/unlock <type>`

**Available lock types:**
• **text** - Text messages
• **media** - All media types
• **photo** - Photos
• **video** - Videos
• **audio** - Audio files
• **voice** - Voice messages
• **document** - Documents
• **sticker** - Stickers
• **gif** - GIFs
• **forward** - Forwarded messages
• **reply** - Replies
• **inline** - Inline keyboards
• **keyboard** - Custom keyboards
• **bot** - Bot messages
• **contact** - Contact sharing
• **location** - Location sharing
• **game** - Games
• **arabic** - Arabic text
• **english** - English text
• **rtl** - Right-to-left text
• **link** - Links
• **username** - Username mentions
• **tag** - Hashtags
• **markdown** - Markdown formatting
• **member** - New members
• **tgservice** - Telegram service messages
• **flood** - Flood protection

**Examples:**
• `/lock photo` - Lock photos
• `/unlock sticker` - Unlock stickers
• `/setflood 3` - Set flood limit to 3 messages"""

# Command mappings
COMMANDS = {
    'lock': handle_lock,
    'unlock': handle_unlock,
    'settings': handle_settings,
    'setflood': handle_setflood,
    'public': handle_public_member,
}

PATTERNS = {}

# Plugin metadata
__plugin_name__ = "Settings"
__plugin_description__ = "Manage group settings and content locks"