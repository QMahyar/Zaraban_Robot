#!/bin/bash
# Zaraban Bot Launcher for Linux/Mac

echo "===================================="
echo "   Starting Zaraban Bot"
echo "===================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "📝 Please copy .env.example to .env and add your BOT_TOKEN"
    echo ""
    exit 1
fi

# Check if dependencies are installed
if ! python3 -c "import telegram" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip3 install -r requirements.txt
    echo ""
fi

# Run the bot
echo "🚀 Starting bot..."
python3 bot.py
