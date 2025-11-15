import os
from dotenv import load_dotenv
from configparser import ConfigParser

load_dotenv()

# Telegram API credentials
API_ID = int(os.getenv('API_ID', '0'))
API_HASH = os.getenv('API_HASH', '')
BOT_TOKEN = os.getenv('BOT_TOKEN', '')

# Data storage configuration (file-based)
DATA_FILE = os.getenv('DATA_FILE', 'data/bot_data.json')

# Bot configuration
BOT_SESSION_NAME = os.getenv('BOT_SESSION_NAME', 'telegram_bot')
SUDO_USERS = list(map(int, os.getenv('SUDO_USERS', '').split(','))) if os.getenv('SUDO_USERS') else []

# Anti-spam settings
FLOOD_LIMIT = int(os.getenv('FLOOD_LIMIT', '5'))
FLOOD_TIME_LIMIT = int(os.getenv('FLOOD_TIME_LIMIT', '2'))
GBAN_LIMIT = int(os.getenv('GBAN_LIMIT', '4'))

# Default help texts
DEFAULT_HELP_TEXT = {
    'en': '''
🤖 **Bot Help**

**Admin Commands:**
• `/ban` - Ban a user
• `/unban` - Unban a user
• `/kick` - Kick a user
• `/mute` - Mute a user
• `/unmute` - Unmute a user
• `/del` - Delete a message
• `/lock [type]` - Lock chat feature
• `/unlock [type]` - Unlock chat feature
• `/settings` - Show group settings

**General Commands:**
• `/help` - Show this help
• `/info` - Get user info
• `/id` - Get chat/user ID

**Sudo Commands:**
• `/sethelp [text]` - Set custom help
• `/delhelp` - Delete custom help
• `/gban` - Global ban user
• `/ungban` - Remove global ban
''',
    'fa': '''
🤖 **راهنمای ربات**

**دستورات مدیریت:**
• `/ban` - مسدود کردن کاربر
• `/unban` - رفع مسدودیت کاربر
• `/kick` - اخراج کاربر
• `/mute` - سکوت کاربر
• `/unmute` - رفع سکوت کاربر
• `/del` - حذف پیام
• `/lock [نوع]` - قفل کردن ویژگی
• `/unlock [نوع]` - باز کردن قفل ویژگی
• `/settings` - تنظیمات گروه

**دستورات عمومی:**
• `/help` - نمایش راهنما
• `/info` - اطلاعات کاربر
• `/id` - شناسه گروه/کاربر

**دستورات سودو:**
• `/sethelp [متن]` - تنظیم راهنمای سفارشی
• `/delhelp` - حذف راهنمای سفارشی
• `/gban` - مسدودیت سراسری
• `/ungban` - رفع مسدودیت سراسری
'''
}

# File paths
DATA_DIR = 'data'
LOGS_DIR = 'data/logs'
TEMP_DIR = 'data/tmp'

# Create directories if they don't exist
for directory in [DATA_DIR, LOGS_DIR, TEMP_DIR]:
    os.makedirs(directory, exist_ok=True)