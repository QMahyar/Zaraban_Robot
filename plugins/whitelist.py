"""
Whitelist plugin - Manage whitelisted users
Ported from the original whitelist.lua
"""

import logging
from utils import UserPermissions, MessageUtils, get_chat_id, get_user_id

logger = logging.getLogger(__name__)

async def handle_whitelist(client, event, args, db):
    """Handle /whitelist command - add user to whitelist"""
    msg = event.message
    chat_id = get_chat_id(msg)
    admin_id = get_user_id(msg)
    
    # Check if user is admin or sudo
    if not await UserPermissions.is_admin(client, chat_id, admin_id) and not UserPermissions.is_sudo(admin_id):
        return "You don't have permission to manage whitelist!"
    
    # Get target user
    target_user = await MessageUtils.get_user_from_message(client, msg, args[0] if args else None)
    if not target_user:
        return "Reply to a user or specify username/ID to whitelist"
    
    # Add to whitelist
    db.add_to_whitelist(target_user.id)
    
    user_name = MessageUtils.user_print_name(target_user)
    return f"✅ User {user_name} [{target_user.id}] has been added to whitelist!"

async def handle_unwhitelist(client, event, args, db):
    """Handle /unwhitelist command - remove user from whitelist"""
    msg = event.message
    chat_id = get_chat_id(msg)
    admin_id = get_user_id(msg)
    
    # Check if user is admin or sudo
    if not await UserPermissions.is_admin(client, chat_id, admin_id) and not UserPermissions.is_sudo(admin_id):
        return "You don't have permission to manage whitelist!"
    
    # Get target user
    target_user = await MessageUtils.get_user_from_message(client, msg, args[0] if args else None)
    if not target_user:
        return "Reply to a user or specify username/ID to remove from whitelist"
    
    # Remove from whitelist
    db.remove_from_whitelist(target_user.id)
    
    user_name = MessageUtils.user_print_name(target_user)
    return f"❌ User {user_name} [{target_user.id}] has been removed from whitelist!"

async def handle_whitelisted(client, event, args, db):
    """Handle /whitelisted command - show whitelisted users"""
    msg = event.message
    chat_id = get_chat_id(msg)
    admin_id = get_user_id(msg)
    
    # Check if user is admin or sudo
    if not await UserPermissions.is_admin(client, chat_id, admin_id) and not UserPermissions.is_sudo(admin_id):
        return "You don't have permission to view whitelist!"
    
    # Get whitelist from database
    # Note: Redis SMEMBERS returns all members of a set
    import redis
    try:
        whitelist_key = "whitelist"
        whitelisted_users = db.redis.smembers(whitelist_key)
        
        if not whitelisted_users:
            return "📝 Whitelist is empty"
        
        response = "**📝 Whitelisted Users:**\n\n"
        
        for user_id in whitelisted_users:
            try:
                user_id = int(user_id)
                user_data = db.get_user(user_id)
                
                if user_data and 'print_name' in user_data:
                    user_name = user_data['print_name']
                else:
                    try:
                        user = await client.get_entity(user_id)
                        user_name = MessageUtils.user_print_name(user)
                    except:
                        user_name = f"User {user_id}"
                
                response += f"• {user_name} (`{user_id}`)\n"
                
            except Exception as e:
                logger.error(f"Error processing whitelisted user {user_id}: {e}")
                response += f"• User {user_id} (error getting name)\n"
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting whitelist: {e}")
        return "❌ Failed to get whitelist"

async def handle_cleanwhitelist(client, event, args, db):
    """Handle /cleanwhitelist command - remove all users from whitelist"""
    msg = event.message
    admin_id = get_user_id(msg)
    
    # Only sudo users can clean whitelist
    if not UserPermissions.is_sudo(admin_id):
        return "Only sudo users can clean the whitelist!"
    
    try:
        # Clear the whitelist set in Redis
        whitelist_key = "whitelist"
        count = db.redis.scard(whitelist_key)  # Get count before clearing
        db.redis.delete(whitelist_key)
        
        return f"🗑️ Whitelist cleaned! Removed {count} users from whitelist."
        
    except Exception as e:
        logger.error(f"Error cleaning whitelist: {e}")
        return "❌ Failed to clean whitelist"

async def handle_checkwhitelist(client, event, args, db):
    """Handle /checkwhitelist command - check if user is whitelisted"""
    msg = event.message
    chat_id = get_chat_id(msg)
    admin_id = get_user_id(msg)
    
    # Check if user is admin or sudo
    if not await UserPermissions.is_admin(client, chat_id, admin_id) and not UserPermissions.is_sudo(admin_id):
        return "You don't have permission to check whitelist!"
    
    # Get target user
    target_user = await MessageUtils.get_user_from_message(client, msg, args[0] if args else None)
    if not target_user:
        return "Reply to a user or specify username/ID to check"
    
    # Check if whitelisted
    is_whitelisted = db.is_whitelisted(target_user.id)
    
    user_name = MessageUtils.user_print_name(target_user)
    status = "✅ IS" if is_whitelisted else "❌ IS NOT"
    
    return f"User {user_name} [{target_user.id}] {status} whitelisted"

# Command mappings
COMMANDS = {
    'whitelist': handle_whitelist,
    'unwhitelist': handle_unwhitelist,
    'whitelisted': handle_whitelisted,
    'cleanwhitelist': handle_cleanwhitelist,
    'checkwhitelist': handle_checkwhitelist,
}

PATTERNS = {}

# Plugin metadata
__plugin_name__ = "Whitelist"
__plugin_description__ = "Manage whitelisted users who are immune to anti-spam"