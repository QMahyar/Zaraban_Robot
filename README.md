# 🤖 Advanced Telegram Moderation Bot

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![Telethon](https://img.shields.io/badge/telethon-1.28%2B-green.svg)](https://github.com/LonamiWebs/Telethon)
[![Redis](https://img.shields.io/badge/redis-4.5%2B-red.svg)](https://redis.io)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

A powerful, modern Telegram group moderation bot built with Python and Telethon. Originally migrated from a legacy telegram-cli/Lua implementation, this bot provides comprehensive anti-spam protection, user management, and administrative tools for Telegram groups and channels.

## 🌟 What This Bot Does

### 🛡️ **Anti-Spam Protection**
- **Smart Flood Detection** - Automatically detects and handles message flooding
- **Global Ban System** - Bans repeat offenders across all managed groups
- **Configurable Limits** - Set custom flood limits per group
- **Whitelist Support** - Exempt trusted users from spam filters

### 👥 **User Management**
- **Ban/Unban** - Permanently restrict troublesome users
- **Kick** - Remove users temporarily
- **Mute/Unmute** - Silence users while keeping them in the group
- **Global Bans** - Ban users across all groups simultaneously
- **User Information** - Get detailed user profiles and statistics

### 🔒 **Content Moderation**
- **Lock System** - Lock/unlock 25+ content types including:
  - Media (photos, videos, audio, documents, stickers, GIFs)
  - Features (forwarding, replies, inline keyboards, bots)
  - Text (Arabic, English, RTL, links, usernames, hashtags)
  - Other (new members, service messages)

### ⚙️ **Group Settings**
- **Customizable Rules** - Configure each group independently
- **Settings Dashboard** - View all group settings at a glance
- **Public Member Lists** - Toggle member list visibility
- **Flood Sensitivity** - Adjust anti-spam sensitivity per group

### 📚 **Help System**
- **Custom Help Text** - Set personalized help messages per group
- **Multi-Language** - Support for English, Persian, and more
- **Hierarchical Help** - Global, group-specific, and owner-specific help texts
- **Dynamic Commands** - Help adapts based on user permissions

### 🔧 **Administrative Tools**
- **Broadcast Messages** - Send announcements to all managed groups
- **Statistics** - View bot usage and performance metrics
- **Log Management** - Comprehensive logging of all moderation actions
- **Migration Tools** - Easy migration from other bot systems

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

## 🚀 Quick Start

### Option 1: Automated Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/telegram-moderation-bot.git
cd telegram-moderation-bot

# Run automated setup
python3 setup.py
```

### Option 2: Manual Installation

#### Prerequisites
- **Python 3.8+** - [Download here](https://python.org/downloads)
- **Redis Server** - [Installation guide](https://redis.io/download)
- **Telegram API Credentials** - [Get from my.telegram.org](https://my.telegram.org)

#### Step-by-Step Setup

1. **Clone and Install Dependencies**
```bash
git clone https://github.com/yourusername/telegram-moderation-bot.git
cd telegram-moderation-bot
pip install -r requirements.txt
```

2. **Get Required Credentials**
   - Visit [my.telegram.org](https://my.telegram.org) and get your `API_ID` and `API_HASH`
   - Message [@BotFather](https://t.me/BotFather) to create a bot and get your `BOT_TOKEN`
   - Get your Telegram user ID (message [@userinfobot](https://t.me/userinfobot))

3. **Configure the Bot**
```bash
cp .env.example .env
nano .env  # Edit with your credentials
```

Example `.env` file:
```env
API_ID=1234567
API_HASH=abcdef1234567890abcdef1234567890
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrSTUvwxyz
SUDO_USERS=123456789,987654321
REDIS_HOST=localhost
REDIS_PORT=6379
FLOOD_LIMIT=5
```

4. **Start Redis Server**
```bash
# Ubuntu/Debian
sudo systemctl start redis-server
sudo systemctl enable redis-server

# macOS with Homebrew
brew services start redis

# Docker
docker run -d --name redis -p 6379:6379 redis:alpine

# Windows (with Redis installed)
redis-server
```

5. **Launch the Bot**
```bash
python3 start.py
```

Or use the convenience script:
```bash
chmod +x run.sh
./run.sh
```

## 📋 Bot Setup Instructions

### 1. **Add Bot to Your Group**
1. Add your bot to the Telegram group
2. Promote the bot to admin with these permissions:
   - Delete messages
   - Ban users
   - Invite users via link
   - Pin messages
   - Manage video chats (optional)

### 2. **Configure Bot Settings**
```bash
# Start the bot and use these commands in your group:
/settings                    # View current group settings
/setflood 5                 # Set flood limit to 5 messages
/lock spam                  # Enable anti-spam protection
/whitelist @username        # Add trusted user to whitelist
```

## 🎮 Commands Reference

### 👥 **User Commands** (Available to everyone)
| Command | Description | Example |
|---------|-------------|---------|
| `/help` | Show help message | `/help` |
| `/info` | Get user information | `/info` or reply to message |
| `/id` | Get user/chat IDs | `/id` |

### 🛡️ **Moderation Commands** (Admins only)
| Command | Description | Example |
|---------|-------------|---------|
| `/ban` | Ban a user | `/ban @username` or reply |
| `/unban` | Unban a user | `/unban @username` |
| `/kick` | Kick a user | `/kick @username` |
| `/mute` | Mute a user | `/mute @username` |
| `/unmute` | Unmute a user | `/unmute @username` |
| `/del` | Delete a message | Reply to message with `/del` |

### ⚙️ **Settings Commands** (Admins only)
| Command | Description | Example |
|---------|-------------|---------|
| `/lock <type>` | Lock content type | `/lock photo`, `/lock sticker` |
| `/unlock <type>` | Unlock content type | `/unlock photo` |
| `/settings` | View group settings | `/settings` |
| `/setflood <number>` | Set flood limit | `/setflood 3` |

### ⚡ **Whitelist Commands** (Admins only)
| Command | Description | Example |
|---------|-------------|---------|
| `/whitelist` | Add user to whitelist | `/whitelist @username` |
| `/unwhitelist` | Remove from whitelist | `/unwhitelist @username` |
| `/whitelisted` | Show whitelisted users | `/whitelisted` |

### 🔧 **Admin Commands** (Sudo users only)
| Command | Description | Example |
|---------|-------------|---------|
| `/gban` | Global ban user | `/gban @username` |
| `/ungban` | Remove global ban | `/ungban @username` |
| `/sethelp <text>` | Set custom help | `/sethelp Welcome to our group!` |
| `/delhelp` | Delete custom help | `/delhelp` |
| `/broadcast <message>` | Broadcast to all chats | `/broadcast Server maintenance tonight` |
| `/stats` | Bot statistics | `/stats` |
| `/leave` | Leave chat | `/leave` |

### 🔒 **Available Lock Types**
**Media:** `photo`, `video`, `audio`, `voice`, `document`, `sticker`, `gif`  
**Features:** `forward`, `reply`, `inline`, `keyboard`, `bot`, `contact`, `location`, `game`  
**Text:** `arabic`, `english`, `rtl`, `link`, `username`, `tag`, `markdown`  
**Other:** `member`, `tgservice`, `flood`

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

## 🚀 Deployment Options

### 🐳 **Docker Deployment**
```bash
# Clone and build
git clone https://github.com/yourusername/telegram-moderation-bot.git
cd telegram-moderation-bot

# Create docker-compose.yml
cat > docker-compose.yml << EOF
version: '3.8'
services:
  redis:
    image: redis:alpine
    restart: unless-stopped
    ports:
      - "6379:6379"
  
  telegram-bot:
    build: .
    restart: unless-stopped
    depends_on:
      - redis
    env_file:
      - .env
    environment:
      - REDIS_HOST=redis
EOF

# Start services
docker-compose up -d
```

### ☁️ **Cloud Deployment**

#### Heroku
```bash
# Install Heroku CLI and login
heroku create your-bot-name
heroku addons:create heroku-redis:hobby-dev
heroku config:set API_ID=your_api_id API_HASH=your_api_hash BOT_TOKEN=your_bot_token
git push heroku main
```

#### VPS/Server
```bash
# Set up systemd service
sudo cp telegram-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```

## 🔧 Advanced Configuration

### **Environment Variables**
```env
# Required
API_ID=1234567                          # From my.telegram.org
API_HASH=abcdef1234567890               # From my.telegram.org  
BOT_TOKEN=123:ABC-DEF123                # From @BotFather
SUDO_USERS=123456789,987654321          # Comma-separated admin IDs

# Optional
REDIS_HOST=localhost                    # Redis server address
REDIS_PORT=6379                         # Redis server port
REDIS_PASSWORD=                         # Redis password (if any)
FLOOD_LIMIT=5                          # Default flood protection limit
GBAN_LIMIT=4                           # Global ban threshold
```

### **Custom Settings Per Group**
```bash
/setflood 3          # Custom flood limit for this group
/lock photo          # Lock photos in this group only
/sethelp Custom help # Group-specific help message
```

## 🐛 Troubleshooting

### **Common Issues & Solutions**

| Problem | Solution |
|---------|----------|
| **Bot doesn't respond** | • Check bot token in `.env`<br>• Ensure bot is admin in group<br>• Verify bot permissions |
| **Redis connection failed** | • Start Redis: `sudo systemctl start redis`<br>• Check Redis settings in `.env`<br>• Test: `redis-cli ping` |
| **Permission denied errors** | • Give bot admin rights<br>• Enable "Delete messages" permission<br>• Enable "Ban users" permission |
| **Flood detection not working** | • Check `/settings` for flood status<br>• Use `/setflood <number>` to configure<br>• Ensure bot is admin |
| **Global ban not working** | • Only sudo users can global ban<br>• Check `SUDO_USERS` in `.env`<br>• Restart bot after config changes |

### **Debug Mode**
```bash
# Enable detailed logging
export LOG_LEVEL=DEBUG
python3 start.py

# Check logs
tail -f bot.log
```

## 🔄 Migration from Other Bots

### **From Original Lua Bot**
```bash
# Use the migration tool
python3 migrate.py backup      # Backup current data
python3 migrate.py migrate     # Import old data
```

### **From Other Python Bots**
1. Export user data (bans, settings)
2. Convert to Redis format
3. Import using migration script

## 📈 Production Tips

### **Performance Optimization**
- Use Redis with persistence enabled
- Set up log rotation
- Monitor memory usage
- Use process managers (systemd/supervisor)

### **Security Best Practices**
- Keep credentials in `.env` file only
- Use strong Redis password
- Regular backups of Redis data
- Monitor bot logs for suspicious activity

### **Scaling**
- Use Redis Cluster for multiple bot instances
- Load balance across multiple servers
- Database sharding for large deployments

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### **Bug Reports**
- Use the issue tracker
- Include error logs and steps to reproduce
- Specify your environment (OS, Python version, etc.)

### **Feature Requests** 
- Open an issue with the `enhancement` label
- Describe the use case and expected behavior
- Consider implementing it yourself!

### **Pull Requests**
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Follow the existing code style
5. Add tests for new functionality
6. Submit a pull request with a clear description

### **Development Setup**
```bash
git clone https://github.com/yourusername/telegram-moderation-bot.git
cd telegram-moderation-bot
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
pre-commit install                    # Code formatting hooks
```

## 📊 Project Stats

![GitHub stars](https://img.shields.io/github/stars/yourusername/telegram-moderation-bot?style=social)
![GitHub forks](https://img.shields.io/github/forks/yourusername/telegram-moderation-bot?style=social)
![GitHub issues](https://img.shields.io/github/issues/yourusername/telegram-moderation-bot)
![GitHub pull requests](https://img.shields.io/github/issues-pr/yourusername/telegram-moderation-bot)

## 🗺️ Roadmap

### **Planned Features**
- [ ] **Web Dashboard** - Web interface for bot management
- [ ] **Analytics** - Usage statistics and reporting  
- [ ] **Plugin Marketplace** - Community plugin repository
- [ ] **Multi-language** - Additional language support
- [ ] **AI Integration** - Smart spam detection with ML
- [ ] **Webhook Support** - Integration with external services

### **Version History**
- **v2.0** - Complete rewrite with Telethon (Current)
- **v1.x** - Original Lua/telegram-cli implementation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Original Developers** - Foundation and core concepts
- **[Telethon](https://github.com/LonamiWebs/Telethon)** - Modern Telegram library
- **[Redis](https://redis.io)** - High-performance database
- **Community Contributors** - Bug reports, feature requests, and improvements

## 📞 Support & Community

### **Get Help**
- 📖 **Documentation** - Check this README first
- 🐛 **Issues** - [Open an issue](https://github.com/yourusername/telegram-moderation-bot/issues) for bugs
- 💡 **Discussions** - [GitHub Discussions](https://github.com/yourusername/telegram-moderation-bot/discussions) for questions
- 💬 **Telegram** - Join our [support group](https://t.me/yoursupportgroup)

### **Stay Updated**
- ⭐ **Star** this repository to show support
- 👀 **Watch** for new releases and updates  
- 🔔 **Follow** [@yourusername](https://github.com/yourusername) for project updates

---

<div align="center">

**🤖 Made with ❤️ for the Telegram community**

*This bot helps thousands of groups maintain a safe and friendly environment*

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/yourusername/telegram-moderation-bot)

</div>

---

> **⚠️ Disclaimer**: This bot is designed for legitimate group moderation. Please use responsibly and follow Telegram's Terms of Service. The developers are not responsible for misuse of this software.