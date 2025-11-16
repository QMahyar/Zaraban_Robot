# 🤖 Zaraban - Lightweight Telegram Bot

**Fast, simple, and clean Telegram bot for local use. No bloat, no databases, just the essentials!**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![python-telegram-bot](https://img.shields.io/badge/python--telegram--bot-21.9-blue)](https://python-telegram-bot.org/)
[![License](https://img.shields.io/badge/license-GPL-green.svg)](LICENSE)

---

## ✨ Features

- ⚡ **Lightning Fast** - Minimal dependencies, maximum performance
- 🎯 **Simple Setup** - Running in under 2 minutes
- 💾 **No Database** - No PostgreSQL, Redis, or complex setup required
- 🔧 **Easy Launcher** - One-click start scripts for Windows, Linux, and Mac
- 🎨 **Interactive UI** - Modern inline keyboards and commands
- 📊 **Built-in Stats** - Track messages and uptime
- 🛠️ **Clean Code** - Well-documented and easy to modify

---

## 🚀 Quick Start

### **1. Get a Bot Token**

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` and follow the instructions
3. Copy your bot token

### **2. Install Dependencies**

```bash
pip install -r requirements.txt
```

### **3. Configure Your Bot**

```bash
cp .env.example .env    # Copy example file
nano .env               # Edit and add your token
```

### **4. Run the Bot**

**Windows:** Double-click `start.bat` or run `python bot.py`
**Linux/Mac:** Run `./start.sh` or `python3 bot.py`

That's it! 🎉

---

## 📋 Commands

- `/start` - Welcome message
- `/help` - Show commands
- `/info` - User information
- `/id` - Get IDs
- `/ping` - Test response
- `/stats` - Bot statistics

---

## 📁 Files

- `bot.py` - Main bot
- `requirements.txt` - Dependencies (only 2!)
- `.env.example` - Config template
- `start.bat/ps1/sh` - Launchers

---

## ⚙️ Configuration

Only need: `BOT_TOKEN=your_token` in `.env`

---

## 💡 Tips

- Keep your token safe!
- Use launcher scripts
- Code is simple and easy to modify
- No databases required!

---

**Made with ❤️ for simple, fast Telegram bots**

**No databases • No bloat • Just works™**
