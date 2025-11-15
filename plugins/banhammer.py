"""
Banhammer plugin - Handle banning, kicking, and user management
Ported from the original banhammer.lua
"""

import logging
from telethon.errors import UserAdminInvalidError, ChatAdminRequiredError, UserNotParticipantError
from telethon.tl.types import ChatBannedRights
from utils import UserPermissions, MessageUtils, ChatLogger, get_chat_id, get_user_id
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

async def handle_ban(client, event, args, db):
    """Handle /ban command"""
    msg = event.message
    chat_id = get_chat_id(msg)
    admin_id = get_user_id(msg)
    
    # Check if user is admin
    if not await UserPermissions.is_admin(client, chat_id, admin_id) and not UserPermissions.is_sudo(admin_id):
        return "You don't have permission to ban users!"
    
    # Get target user
    target_user = await MessageUtils.get_user_from_message(client, msg, args[0] if args else None)
    if not target_user:
        return "Reply to a user or specify username/ID to ban"
    
    # Check if target is admin
    if await UserPermissions.is_admin(client, chat_id, target_user.id):
        return "Cannot ban admin users!"
    
    # Check if target is sudo
    if UserPermissions.is_sudo(target_user.id):
        return "Cannot ban sudo users!"
    
    try:
        # Ban user
        await client.edit_permissions(chat_id, target_user.id, view_messages=False)
        
        # Save ban to database
        db.ban_user(target_user.id, chat_id, admin_id)
        
        # Log action
        ChatLogger.log_action(chat_id, f"User {target_user.id} banned by {admin_id}")
        
        user_name = MessageUtils.user_print_name(target_user)
        return f"User {user_name} [{target_user.id}] has been banned!"
        
    except (UserAdminInvalidError, ChatAdminRequiredError):
        return "I don't have permission to ban users!"
    except Exception as e:
        logger.error(f"Error banning user: {e}")
        return "Failed to ban user!"

async def handle_unban(client, event, args, db):
    """Handle /unban command"""
    msg = event.message
    chat_id = get_chat_id(msg)
    admin_id = get_user_id(msg)
    
    # Check if user is admin
    if not await UserPermissions.is_admin(client, chat_id, admin_id) and not UserPermissions.is_sudo(admin_id):
        return "You don't have permission to unban users!"
    
    # Get target user
    target_user = await MessageUtils.get_user_from_message(client, msg, args[0] if args else None)
    if not target_user:
        return "Reply to a user or specify username/ID to unban"
    
    try:
        # Unban user
        await client.edit_permissions(chat_id, target_user.id, view_messages=True)
        
        # Remove ban from database
        db.unban_user(target_user.id, chat_id)
        
        # Log action
        ChatLogger.log_action(chat_id, f"User {target_user.id} unbanned by {admin_id}")
        
        user_name = MessageUtils.user_print_name(target_user)
        return f"User {user_name} [{target_user.id}] has been unbanned!"
        
    except Exception as e:
        logger.error(f"Error unbanning user: {e}")
        return "Failed to unban user!"

async def handle_kick(client, event, args, db):
    """Handle /kick command"""
    msg = event.message
    chat_id = get_chat_id(msg)
    admin_id = get_user_id(msg)
    
    # Check if user is admin
    if not await UserPermissions.is_admin(client, chat_id, admin_id) and not UserPermissions.is_sudo(admin_id):
        return "You don't have permission to kick users!"
    
    # Get target user
    target_user = await MessageUtils.get_user_from_message(client, msg, args[0] if args else None)
    if not target_user:
        return "Reply to a user or specify username/ID to kick"
    
    # Check if target is admin
    if await UserPermissions.is_admin(client, chat_id, target_user.id):
        return "Cannot kick admin users!"
    
    # Check if target is sudo
    if UserPermissions.is_sudo(target_user.id):
        return "Cannot kick sudo users!"
    
    try:
        # Kick user (ban then unban)
        await client.kick_participant(chat_id, target_user.id)
        
        # Log action
        ChatLogger.log_action(chat_id, f"User {target_user.id} kicked by {admin_id}")
        
        user_name = MessageUtils.user_print_name(target_user)
        return f"User {user_name} [{target_user.id}] has been kicked!"
        
    except (UserAdminInvalidError, ChatAdminRequiredError):
        return "I don't have permission to kick users!"
    except Exception as e:
        logger.error(f"Error kicking user: {e}")
        return "Failed to kick user!"

async def handle_mute(client, event, args, db):
    """Handle /mute command"""
    msg = event.message
    chat_id = get_chat_id(msg)
    admin_id = get_user_id(msg)
    
    # Check if user is admin
    if not await UserPermissions.is_admin(client, chat_id, admin_id) and not UserPermissions.is_sudo(admin_id):
        return "You don't have permission to mute users!"
    
    # Get target user
    target_user = await MessageUtils.get_user_from_message(client, msg, args[0] if args else None)
    if not target_user:
        return "Reply to a user or specify username/ID to mute"
    
    # Check if target is admin
    if await UserPermissions.is_admin(client, chat_id, target_user.id):
        return "Cannot mute admin users!"
    
    # Check if target is sudo
    if UserPermissions.is_sudo(target_user.id):
        return "Cannot mute sudo users!"
    
    try:
        # Mute user (restrict sending messages)
        banned_rights = ChatBannedRights(
            until_date=None,
            send_messages=True
        )
        await client.edit_permissions(chat_id, target_user.id, banned_rights)
        
        # Log action
        ChatLogger.log_action(chat_id, f"User {target_user.id} muted by {admin_id}")
        
        user_name = MessageUtils.user_print_name(target_user)
        return f"User {user_name} [{target_user.id}] has been muted!"
        
    except (UserAdminInvalidError, ChatAdminRequiredError):
        return "I don't have permission to mute users!"
    except Exception as e:
        logger.error(f"Error muting user: {e}")
        return "Failed to mute user!"

async def handle_unmute(client, event, args, db):
    """Handle /unmute command"""
    msg = event.message
    chat_id = get_chat_id(msg)
    admin_id = get_user_id(msg)
    
    # Check if user is admin
    if not await UserPermissions.is_admin(client, chat_id, admin_id) and not UserPermissions.is_sudo(admin_id):
        return "You don't have permission to unmute users!"
    
    # Get target user
    target_user = await MessageUtils.get_user_from_message(client, msg, args[0] if args else None)
    if not target_user:
        return "Reply to a user or specify username/ID to unmute"
    
    try:
        # Unmute user (remove restrictions)
        await client.edit_permissions(chat_id, target_user.id, send_messages=True)
        
        # Log action
        ChatLogger.log_action(chat_id, f"User {target_user.id} unmuted by {admin_id}")
        
        user_name = MessageUtils.user_print_name(target_user)
        return f"User {user_name} [{target_user.id}] has been unmuted!"
        
    except Exception as e:
        logger.error(f"Error unmuting user: {e}")
        return "Failed to unmute user!"

async def handle_gban(client, event, args, db):
    """Handle /gban command (global ban)"""
    msg = event.message
    admin_id = get_user_id(msg)
    
    # Only sudo users can global ban
    if not UserPermissions.is_sudo(admin_id):
        return "Only sudo users can use global ban!"
    
    # Get target user
    target_user = await MessageUtils.get_user_from_message(client, msg, args[0] if args else None)
    if not target_user:
        return "Reply to a user or specify username/ID to globally ban"
    
    # Check if target is sudo
    if UserPermissions.is_sudo(target_user.id):
        return "Cannot globally ban sudo users!"
    
    # Add to global ban list
    db.gban_user(target_user.id)
    
    user_name = MessageUtils.user_print_name(target_user)
    return f"User {user_name} [{target_user.id}] has been globally banned!"

async def handle_ungban(client, event, args, db):
    """Handle /ungban command (remove global ban)"""
    msg = event.message
    admin_id = get_user_id(msg)
    
    # Only sudo users can remove global ban
    if not UserPermissions.is_sudo(admin_id):
        return "Only sudo users can remove global ban!"
    
    # Get target user
    target_user = await MessageUtils.get_user_from_message(client, msg, args[0] if args else None)
    if not target_user:
        return "Reply to a user or specify username/ID to remove global ban"
    
    # Remove from global ban list
    db.ungban_user(target_user.id)
    
    user_name = MessageUtils.user_print_name(target_user)
    return f"User {user_name} [{target_user.id}] has been removed from global ban list!"

async def handle_del(client, event, args, db):
    """Handle /del command (delete message)"""
    msg = event.message
    chat_id = get_chat_id(msg)
    admin_id = get_user_id(msg)
    
    # Check if user is admin
    if not await UserPermissions.is_admin(client, chat_id, admin_id) and not UserPermissions.is_sudo(admin_id):
        return "You don't have permission to delete messages!"
    
    # Check if replying to a message
    if not msg.reply_to_msg_id:
        return "Reply to a message to delete it"
    
    try:
        # Delete the replied message
        await client.delete_messages(chat_id, msg.reply_to_msg_id)
        
        # Delete the command message too
        await msg.delete()
        
        # Log action
        ChatLogger.log_action(chat_id, f"Message {msg.reply_to_msg_id} deleted by {admin_id}")
        
        return None  # Don't send response since we deleted the command
        
    except Exception as e:
        logger.error(f"Error deleting message: {e}")
        return "Failed to delete message!"

async def pre_process(client, msg, db):
    """Check for globally banned users"""
    user_id = get_user_id(msg)
    chat_id = get_chat_id(msg)
    
    if not user_id or not chat_id or chat_id == user_id:  # Skip private chats
        return True
    
    # Check if user is globally banned
    if db.is_gbanned(user_id):
        try:
            # Kick the banned user
            await client.kick_participant(chat_id, user_id)
            
            # Send notification
            user = await client.get_entity(user_id)
            user_name = MessageUtils.user_print_name(user)
            await client.send_message(chat_id, f"User {user_name} [{user_id}] is globally banned and has been removed!")
            
            return False  # Block the message
        except:
            pass
    
    return True

# Command mappings
COMMANDS = {
    'ban': handle_ban,
    'unban': handle_unban,
    'kick': handle_kick,
    'mute': handle_mute,
    'unmute': handle_unmute,
    'gban': handle_gban,
    'ungban': handle_ungban,
    'del': handle_del,
}

PATTERNS = {}

# Plugin metadata
__plugin_name__ = "Banhammer"
__plugin_description__ = "User moderation tools - ban, kick, mute, and global ban system"