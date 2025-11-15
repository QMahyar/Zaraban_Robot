#!/usr/bin/env python3
"""
Modern Telegram Bot - Telethon Edition
Migrated from legacy telegram-cli bot

Usage: python3 start.py
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bot.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Reduce telethon logging noise
    logging.getLogger('telethon').setLevel(logging.WARNING)

def check_requirements():
    """Check if all required modules are available"""
    required_modules = [
        'telethon',
        'aiohttp',
        'python-dotenv'
    ]
    
    missing = []
    for module in required_modules:
        try:
            __import__(module.replace('-', '_'))
        except ImportError:
            missing.append(module)
    
    if missing:
        print(f"Missing required modules: {', '.join(missing)}")
        print("Install them with: pip install -r requirements.txt")
        sys.exit(1)

def check_config():
    """Check if configuration is valid"""
    from config import API_ID, API_HASH, BOT_TOKEN
    
    if not API_ID or API_ID == 0:
        print("ERROR: API_ID not configured!")
        print("Get your API credentials from https://my.telegram.org")
        sys.exit(1)
    
    if not API_HASH:
        print("ERROR: API_HASH not configured!")
        print("Get your API credentials from https://my.telegram.org")
        sys.exit(1)
    
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN not configured!")
        print("Get a bot token from @BotFather on Telegram")
        sys.exit(1)

def check_storage():
    """Check data storage"""
    try:
        from database import db
        # Test database operations
        test_data = db._load_data()
        print("✅ File-based storage ready")
    except Exception as e:
        print(f"❌ Storage initialization failed: {e}")
        print("Check data directory permissions")
        sys.exit(1)

def create_system_files():
    """Create system files if they don't exist"""
    system_dir = project_root / "system"
    system_dir.mkdir(exist_ok=True)
    
    # Create team file
    team_file = system_dir / "team"
    if not team_file.exists():
        team_file.write_text("YourTeamName")
    
    # Create channel file
    channel_file = system_dir / "channel"
    if not channel_file.exists():
        channel_file.write_text("@YourChannel")
    
    print("✅ System files created")

async def main():
    """Main function to start the bot"""
    print("🤖 Starting Modern Telegram Bot...")
    
    # Setup
    setup_logging()
    logger = logging.getLogger(__name__)
    
    print("🔍 Checking requirements...")
    check_requirements()
    
    print("⚙️  Checking configuration...")
    check_config()
    
    print("🔌 Checking data storage...")
    check_storage()
    
    print("📁 Creating system files...")
    create_system_files()
    
    # Start bot
    try:
        from bot import bot
        print("🚀 Starting bot...")
        await bot.run()
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"💥 Bot crashed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"💥 Startup failed: {e}")
        sys.exit(1)