#!/usr/bin/env python3
"""
Zaraban - Modern Telegram Bot for Local Use
Simple, fast, and clean - no databases required
Updated for python-telegram-bot 21.x
"""

import logging
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MinimalBot:
    def __init__(self, token: str):
        self.token = token
        self.stats = {
            'messages_processed': 0,
            'commands_executed': 0,
            'start_time': datetime.now()
        }
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        chat = update.effective_chat
        
        self.stats['commands_executed'] += 1
        
        if chat.type == 'private':
            welcome_text = (
                f"👋 **Hello {user.first_name}!**\n\n"
                f"🤖 I'm Zaraban - your lightweight Telegram bot\n"
                f"⚡ Fast, simple, and clean - no bloat!\n\n"
                f"**📋 Available Commands:**\n"
                f"• `/start` - Show this message\n"
                f"• `/help` - Get detailed help\n"
                f"• `/ping` - Test bot response\n"
                f"• `/info` - User information\n"
                f"• `/id` - Get chat/user IDs\n"
                f"• `/stats` - Bot statistics\n\n"
                f"🎯 Add me to groups for group management features!"
            )
            
            # Add inline keyboard
            keyboard = [
                [
                    InlineKeyboardButton("📘 Help", callback_data="help"),
                    InlineKeyboardButton("⚙️ Settings", callback_data="settings")
                ],
                [
                    InlineKeyboardButton("📊 Stats", callback_data="stats"),
                    InlineKeyboardButton("🔗 Add to Group", 
                                       url=f"https://t.me/{context.bot.username}?startgroup=true")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                welcome_text, 
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            # Group start message
            group_text = (
                f"👋 **Hello everyone!**\n\n"
                f"🤖 Zaraban is now active in **{chat.title}**\n\n"
                f"✨ **What I can do:**\n"
                f"• 🔍 User info and IDs\n"
                f"• 📊 Group statistics\n"
                f"• ⚡ Quick responses\n"
                f"• 💬 Interactive commands\n\n"
                f"Type /help to see all commands"
            )
            
            await update.message.reply_text(group_text, parse_mode=ParseMode.MARKDOWN)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help message"""
        self.stats['commands_executed'] += 1
        
        chat = update.effective_chat
        
        if chat.type == 'private':
            help_text = (
                "📖 **Zaraban Bot - Command Help**\n\n"
                "ℹ️ **Information Commands:**\n"
                "• `/start` - Welcome message\n"
                "• `/help` - This help message\n"
                "• `/info` - Get user information\n"
                "• `/id` - Get chat and user IDs\n\n"
                "🔧 **Utility Commands:**\n"
                "• `/ping` - Test bot response time\n"
                "• `/stats` - View bot statistics\n\n"
                "👥 **Group Commands:**\n"
                "• All above commands work in groups\n"
                "• Reply to messages for user-specific info\n\n"
                "⚡ **Fast, simple, and lightweight!**"
            )
        else:
            help_text = (
                "📖 **Available Commands**\n\n"
                "• `/help` - Show this message\n"
                "• `/info` - User information\n"
                "• `/id` - Get chat/user IDs\n"
                "• `/stats` - Bot statistics\n"
                "• `/ping` - Test response\n\n"
                "💬 DM me for detailed help!"
            )
        
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Demo settings command"""
        self.stats['commands_executed'] += 1
        
        settings_text = (
            "⚙️ **Bot Settings (Demo)**\n\n"
            "🌐 Language: English\n"
            "🛡️ Anti-spam: ✅ Enabled\n"
            "👋 Welcome: ✅ Enabled\n"
            "📊 Analytics: ✅ Enabled\n"
            "🔒 Locks: None\n\n"
            "💡 In the full version, you can:\n"
            "• Customize all settings\n"
            "• Set up welcome messages\n"
            "• Configure moderation\n"
            "• Manage filters\n"
            "• And much more!"
        )
        
        # Demo keyboard
        keyboard = [
            [
                InlineKeyboardButton("🌐 Language", callback_data="demo_language"),
                InlineKeyboardButton("🛡️ Security", callback_data="demo_security")
            ],
            [
                InlineKeyboardButton("👋 Welcome", callback_data="demo_welcome"),
                InlineKeyboardButton("📊 Analytics", callback_data="demo_analytics")
            ],
            [
                InlineKeyboardButton("❌ Close", callback_data="close")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            settings_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )

    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show bot statistics"""
        self.stats['commands_executed'] += 1
        
        uptime = datetime.now() - self.stats['start_time']
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        stats_text = (
            f"📊 **Bot Statistics**\n\n"
            f"🕐 **Uptime:** {hours}h {minutes}m {seconds}s\n"
            f"💬 **Messages:** {self.stats['messages_processed']}\n"
            f"⚡ **Commands:** {self.stats['commands_executed']}\n"
            f"🚀 **Started:** {self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"🤖 **Version:** {self.version}\n"
            f"🔗 **Framework:** python-telegram-bot 21.9"
        )
        
        await update.message.reply_text(stats_text, parse_mode=ParseMode.MARKDOWN)

    async def ping_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Test bot response"""
        self.stats['commands_executed'] += 1
        
        start_time = datetime.now()
        message = await update.message.reply_text("🏓 Pong!")
        end_time = datetime.now()
        
        response_time = (end_time - start_time).total_seconds() * 1000
        
        await message.edit_text(f"🏓 Pong!\n⚡ Response time: {response_time:.0f}ms")

    async def info_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get user information"""
        self.stats['commands_executed'] += 1
        
        user = update.effective_user
        chat = update.effective_chat
        
        info_text = (
            f"👤 **User Information**\n\n"
            f"**Name:** {user.full_name}\n"
            f"**ID:** `{user.id}`\n"
        )
        
        if user.username:
            info_text += f"**Username:** @{user.username}\n"
            
        info_text += f"**Chat:** {chat.title or 'Private Chat'}\n"
        info_text += f"**Chat ID:** `{chat.id}`\n"
        info_text += f"**Chat Type:** {chat.type}\n"
        
        await update.message.reply_text(info_text, parse_mode=ParseMode.MARKDOWN)

    async def id_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get IDs"""
        self.stats['commands_executed'] += 1
        
        user = update.effective_user
        chat = update.effective_chat
        
        id_text = (
            f"🆔 **Chat & User IDs**\n\n"
            f"**Your ID:** `{user.id}`\n"
            f"**Chat ID:** `{chat.id}`\n"
        )
        
        if update.message.reply_to_message:
            replied_user = update.message.reply_to_message.from_user
            id_text += f"**Replied User ID:** `{replied_user.id}`\n"
        
        await update.message.reply_text(id_text, parse_mode=ParseMode.MARKDOWN)

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "help":
            await self.help_command(query, context)
        elif query.data == "settings":
            await self.settings_command(query, context)
        elif query.data == "stats":
            await self.stats_command(query, context)
        elif query.data.startswith("demo_"):
            demo_type = query.data.replace("demo_", "")
            await query.edit_message_text(
                f"🔧 **{demo_type.title()} Settings**\n\n"
                f"This is a demo of the {demo_type} configuration interface.\n\n"
                f"In the full version, you would have:\n"
                f"• Interactive configuration options\n"
                f"• Real-time settings updates\n"
                f"• Advanced customization\n"
                f"• Save/load presets\n\n"
                f"💡 Contact support to get the full version!",
                parse_mode=ParseMode.MARKDOWN
            )
        elif query.data == "close":
            await query.edit_message_text("⚙️ Settings menu closed.")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages - just count them"""
        self.stats['messages_processed'] += 1
        # Bot silently processes messages, responds only to commands

def main():
    """Main function to start the bot"""
    print("╔══════════════════════════════╗")
    print("║   🤖 ZARABAN BOT v2.0.0    ║")
    print("╚══════════════════════════════╝")
    print()
    
    # Check for bot token
    token = os.getenv("BOT_TOKEN")
    
    if not token:
        print("❌ Error: BOT_TOKEN not found!")
        print("")
        print("🔑 Please set your bot token:")
        print("   Windows (PowerShell): $env:BOT_TOKEN='your_token'")
        print("   Windows (CMD): set BOT_TOKEN=your_token")
        print("   Linux/Mac: export BOT_TOKEN='your_token'")
        print("")
        print("💡 Or create a .env file with: BOT_TOKEN=your_token")
        print("👤 Get a token from @BotFather on Telegram")
        return
    
    if token.startswith("123456"):
        print("⚠️  Warning: Using example token")
        print("👉 Get a real token from @BotFather on Telegram")
        print()
    
    print("✅ Token loaded")
    print("⏳ Initializing bot...")
    
    # Create bot instance
    bot = ZarabanBot(token)
    
    # Create application
    application = Application.builder().token(token).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", bot.start_command))
    application.add_handler(CommandHandler("help", bot.help_command))
    application.add_handler(CommandHandler("stats", bot.stats_command))
    application.add_handler(CommandHandler("ping", bot.ping_command))
    application.add_handler(CommandHandler("info", bot.info_command))
    application.add_handler(CommandHandler("id", bot.id_command))
    
    # Callback handler for inline buttons
    application.add_handler(CallbackQueryHandler(bot.handle_callback))
    
    # Message handler (for stats tracking)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    
    print("✅ Bot configured successfully")
    print("✅ All handlers registered")
    print()
    print("🚀 Bot is now running...")
    print("⏹️  Press Ctrl+C to stop")
    print()
    
    try:
        # Run bot with polling
        application.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)
    except KeyboardInterrupt:
        print("\n\n⏹️  Bot stopped by user")
        print("👋 Goodbye!")
    except Exception as e:
        print(f"\n\n❌ Bot error: {e}")
        print("💡 Check your token and internet connection")

if __name__ == "__main__":
    main()