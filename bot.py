import asyncio
import logging
import os
import importlib
import importlib.util
import sys
from typing import Dict, List, Callable, Any
from telethon import TelegramClient, events
from telethon.tl.types import MessageEntityMention, MessageEntityTextUrl
from database import db
from utils import UserPermissions, MessageUtils, AntiSpam, ChatLogger, get_chat_id, get_user_id
from config import API_ID, API_HASH, BOT_TOKEN, BOT_SESSION_NAME, FLOOD_LIMIT, GBAN_LIMIT

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.client = TelegramClient(BOT_SESSION_NAME, API_ID, API_HASH)
        self.plugins: Dict[str, Any] = {}
        self.command_handlers: Dict[str, Callable] = {}
        self.pattern_handlers: List[tuple] = []
        self.pre_processors: List[Callable] = []
        self.started = False
        
    async def start(self):
        """Start the bot"""
        await self.client.start(bot_token=BOT_TOKEN)
        self.started = True
        
        # Get bot info
        me = await self.client.get_me()
        logger.info(f"Bot started as @{me.username}")
        
        # Load plugins
        await self.load_plugins()
        
        # Register event handlers
        self.register_handlers()
        
        # Set up cron jobs
        asyncio.create_task(self.cron_scheduler())
        
        logger.info("Bot is ready!")
        
    async def load_plugins(self):
        """Load all plugins from plugins directory"""
        plugins_dir = 'plugins'
        if not os.path.exists(plugins_dir):
            os.makedirs(plugins_dir)
            return
            
        for filename in os.listdir(plugins_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                plugin_name = filename[:-3]
                try:
                    # Import plugin module
                    spec = importlib.util.spec_from_file_location(
                        plugin_name, 
                        os.path.join(plugins_dir, filename)
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Register plugin
                    self.plugins[plugin_name] = module
                    
                    # Register commands from plugin
                    if hasattr(module, 'COMMANDS'):
                        for command, handler in module.COMMANDS.items():
                            self.command_handlers[command] = handler
                    
                    # Register patterns from plugin
                    if hasattr(module, 'PATTERNS'):
                        for pattern, handler in module.PATTERNS.items():
                            self.pattern_handlers.append((pattern, handler))
                    
                    # Register pre-processors
                    if hasattr(module, 'pre_process'):
                        self.pre_processors.append(module.pre_process)
                        
                    logger.info(f"Loaded plugin: {plugin_name}")
                    
                except Exception as e:
                    logger.error(f"Failed to load plugin {plugin_name}: {e}")
    
    def register_handlers(self):
        """Register Telethon event handlers"""
        
        @self.client.on(events.NewMessage)
        async def message_handler(event):
            if not self.started:
                return
                
            try:
                await self.process_message(event)
            except Exception as e:
                logger.error(f"Error processing message: {e}")
        
        @self.client.on(events.ChatAction)
        async def chat_action_handler(event):
            try:
                await self.process_chat_action(event)
            except Exception as e:
                logger.error(f"Error processing chat action: {e}")
    
    async def process_message(self, event):
        """Process incoming messages"""
        msg = event.message
        
        # Skip service messages initially
        if msg.action:
            return await self.process_service_message(event)
        
        # Skip messages from self
        if msg.sender_id == (await self.client.get_me()).id:
            return
            
        # Save user info
        await self.save_user_info(msg)
        
        # Run pre-processors (anti-spam, etc.)
        for pre_processor in self.pre_processors:
            try:
                result = await pre_processor(self.client, msg, db)
                if result is False:  # Message should be blocked
                    return
            except Exception as e:
                logger.error(f"Error in pre-processor: {e}")
        
        # Process commands and patterns
        await self.match_patterns(event)
        
        # Mark as read if enabled
        if db.get_bot_setting('markread') == 'on':
            await event.message.mark_read()
    
    async def process_service_message(self, event):
        """Process service messages (joins, leaves, etc.)"""
        msg = event.message
        chat_id = get_chat_id(msg)
        
        if msg.action:
            # Log service actions
            action_type = type(msg.action).__name__
            ChatLogger.log_action(chat_id, f"Service action: {action_type}")
            
            # Handle new members
            if hasattr(msg.action, 'users'):
                for user_id in msg.action.users:
                    # Check if globally banned
                    if db.is_gbanned(user_id):
                        try:
                            await self.client.kick_participant(chat_id, user_id)
                            await event.respond("User was globally banned and has been removed.")
                        except:
                            pass
    
    async def process_chat_action(self, event):
        """Process chat actions (joins, leaves, etc.)"""
        chat_id = get_chat_id(event.original_update)
        
        # Log chat actions
        if event.user_joined or event.user_added:
            user_id = event.user_id
            ChatLogger.log_action(chat_id, f"User {user_id} joined/was added")
            
            # Check global ban
            if db.is_gbanned(user_id):
                try:
                    await self.client.kick_participant(chat_id, user_id)
                    await self.client.send_message(chat_id, "User was globally banned and has been removed.")
                except:
                    pass
                    
        elif event.user_left or event.user_kicked:
            user_id = event.user_id
            ChatLogger.log_action(chat_id, f"User {user_id} left/was kicked")
    
    async def save_user_info(self, msg):
        """Save user information to database"""
        user_id = get_user_id(msg)
        chat_id = get_chat_id(msg)
        
        if user_id:
            try:
                user = await self.client.get_entity(user_id)
                user_data = {
                    'id': str(user.id),
                    'first_name': getattr(user, 'first_name', ''),
                    'last_name': getattr(user, 'last_name', ''),
                    'username': getattr(user, 'username', ''),
                    'print_name': MessageUtils.user_print_name(user)
                }
                db.save_user(user_id, user_data)
                
                # Add to chat users
                if chat_id:
                    db.add_chat_user(chat_id, user_id)
                    
                # Increment message count
                db.increment_user_chat_msgs(user_id, chat_id or 0)
                
            except Exception as e:
                logger.error(f"Error saving user info: {e}")
    
    async def match_patterns(self, event):
        """Match message against command patterns"""
        text = event.message.text or event.message.caption or ""
        
        # Try command handlers first
        if text.startswith(('/', '!', '#')):
            parts = text.split()
            command = parts[0][1:].lower()  # Remove prefix and lowercase
            args = parts[1:] if len(parts) > 1 else []
            
            if command in self.command_handlers:
                try:
                    handler = self.command_handlers[command]
                    result = await handler(self.client, event, args, db)
                    if result:
                        await event.respond(result)
                except Exception as e:
                    logger.error(f"Error in command handler {command}: {e}")
                return
        
        # Try pattern handlers
        for pattern, handler in self.pattern_handlers:
            try:
                import re
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    result = await handler(self.client, event, match.groups(), db)
                    if result:
                        await event.respond(result)
                    break
            except Exception as e:
                logger.error(f"Error in pattern handler: {e}")
    
    async def cron_scheduler(self):
        """Run periodic tasks"""
        while True:
            try:
                # Run cron tasks from plugins
                for plugin_name, plugin in self.plugins.items():
                    if hasattr(plugin, 'cron'):
                        try:
                            await plugin.cron(self.client, db)
                        except Exception as e:
                            logger.error(f"Error in cron for {plugin_name}: {e}")
                
                # Wait 5 minutes
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Error in cron scheduler: {e}")
                await asyncio.sleep(60)
    
    async def run(self):
        """Run the bot"""
        await self.start()
        await self.client.run_until_disconnected()

# Create global bot instance
bot = TelegramBot()

if __name__ == '__main__':
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        sys.exit(1)