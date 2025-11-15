# Modern Telegram Bot - Telethon Edition

A modern, feature-rich Telegram bot migrated from the legacy telegram-cli to Telethon with all original functionalities preserved and enhanced.

## 🚀 Features

### Core Features
- **Anti-Spam Protection** - Advanced flood detection and automatic user management
- **User Management** - Ban, kick, mute, and global ban system
- **Content Moderation** - Lock/unlock various content types and features
- **Help System** - Customizable help texts with multi-language support
- **Whitelist System** - Exempt trusted users from anti-spam measures
- **Admin Tools** - Comprehensive moderation and management commands

### New Improvements
- **Modern Python** - Built with Telethon, the most advanced Telegram library
- **Async/Await** - Fully asynchronous for better performance
- **Redis Database** - Efficient data storage and retrieval
- **Plugin System** - Modular design for easy customization
- **Better Logging** - Comprehensive logging and error tracking
- **Configuration** - Easy environment-based configuration

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- Redis server
- Telegram API credentials

### Step 1: Clone and Setup
```bash
git clone <repository-url>
cd telegram-bot-modern
pip install -r requirements.txt
```

### Step 2: Configuration
1. Copy the example configuration:
```bash
cp .env.example .env
```

2. Get your Telegram API credentials from https://my.telegram.org
3. Get a bot token from @BotFather
4. Edit `.env` with your credentials:

```env
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
SUDO_USERS=your_user_id,another_user_id
```

### Step 3: Start Redis
```bash
# Ubuntu/Debian
sudo systemctl start redis-server

# Or using Docker
docker run -d -p 6379:6379 redis:alpine
```

### Step 4: Run the Bot
```bash
python3 start.py
```

## 🎮 Commands

### User Commands
- `/help` - Show help message
- `/info` - Get user information
- `/id` - Get user/chat IDs
- `/chatinfo` - Get chat information

### Moderation Commands
- `/ban` - Ban a user
- `/unban` - Unban a user
- `/kick` - Kick a user
- `/mute` - Mute a user
- `/unmute` - Unmute a user
- `/del` - Delete a message

### Settings Commands
- `/lock <type>` - Lock content type
- `/unlock <type>` - Unlock content type
- `/settings` - View group settings
- `/setflood <number>` - Set flood limit

### Whitelist Commands
- `/whitelist` - Add user to whitelist
- `/unwhitelist` - Remove from whitelist
- `/whitelisted` - Show whitelisted users

### Admin Commands (Sudo Users Only)
- `/gban` - Global ban user
- `/ungban` - Remove global ban
- `/sethelp <text>` - Set custom help
- `/delhelp` - Delete custom help
- `/broadcast <message>` - Broadcast to all chats
- `/stats` - Bot statistics
- `/leave` - Leave chat

## 🔧 Configuration Options

### Environment Variables
- `API_ID` - Telegram API ID
- `API_HASH` - Telegram API Hash
- `BOT_TOKEN` - Bot token from BotFather
- `REDIS_HOST` - Redis server host (default: localhost)
- `REDIS_PORT` - Redis server port (default: 6379)
- `SUDO_USERS` - Comma-separated list of sudo user IDs
- `FLOOD_LIMIT` - Default flood limit (default: 5)
- `GBAN_LIMIT` - Global ban threshold (default: 4)

### Lock Types
The bot supports locking various content types:
- `text`, `media`, `photo`, `video`, `audio`, `voice`
- `document`, `sticker`, `gif`, `forward`, `reply`
- `inline`, `keyboard`, `bot`, `contact`, `location`
- `game`, `arabic`, `english`, `rtl`, `link`
- `username`, `tag`, `markdown`, `member`, `tgservice`

## 🏗️ Architecture

### Core Components
- **bot.py** - Main bot framework and event handling
- **database.py** - Redis database interface
- **utils.py** - Utility functions and helpers
- **config.py** - Configuration management

### Plugin System
The bot uses a modular plugin system:
- **plugins/anti_spam.py** - Anti-spam protection
- **plugins/banhammer.py** - User management
- **plugins/help.py** - Help system
- **plugins/info.py** - User/chat information
- **plugins/settings.py** - Group settings
- **plugins/sudo.py** - Admin commands
- **plugins/whitelist.py** - Whitelist management

## 🔄 Migration from Legacy Bot

This bot maintains compatibility with the original Lua-based bot:
- All commands work the same way
- Database schema is preserved
- Settings and configurations are migrated
- Plugin functionality is equivalent or improved

### Key Improvements
1. **Performance** - Async operations for better speed
2. **Reliability** - Better error handling and recovery
3. **Maintainability** - Clean, modern Python code
4. **Extensibility** - Easy to add new features
5. **Security** - Updated security practices

## 🐛 Troubleshooting

### Common Issues

**Bot doesn't respond:**
- Check if bot token is correct
- Verify bot is added to the group
- Check bot has necessary permissions

**Database errors:**
- Ensure Redis is running
- Check Redis connection settings
- Verify Redis authentication if used

**Permission errors:**
- Make sure bot has admin rights
- Check if bot can delete messages
- Verify ban/kick permissions

### Logs
Check `bot.log` for detailed error information:
```bash
tail -f bot.log
```

## 📝 Development

### Adding New Plugins
1. Create a new file in `plugins/` directory
2. Implement command handlers and patterns
3. Export `COMMANDS` and `PATTERNS` dictionaries
4. Restart the bot to load the plugin

### Example Plugin Structure
```python
async def handle_command(client, event, args, db):
    # Command logic here
    return "Response message"

COMMANDS = {
    'mycommand': handle_command
}

PATTERNS = {}
```

## 📄 License

This project is licensed under the same terms as the original project.

## 🙏 Credits

- Original bot developers for the foundation
- Telethon library developers
- Python and Redis communities

## 📞 Support

For support and questions:
- Open an issue on GitHub
- Check the documentation
- Contact the development team

---

**Note:** This is a complete rewrite using modern technologies while preserving all original functionality. The bot is production-ready and actively maintained.