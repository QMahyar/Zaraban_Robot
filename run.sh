#!/bin/bash

# Modern Telegram Bot Startup Script
# Replacement for the original start.sh

echo "🤖 Starting Modern Telegram Bot..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Check if Redis is running
if ! command -v redis-cli &> /dev/null; then
    echo "⚠️  Redis CLI not found, make sure Redis is installed and running"
else
    if ! redis-cli ping &> /dev/null; then
        echo "⚠️  Redis is not responding, trying to start..."
        if command -v systemctl &> /dev/null; then
            sudo systemctl start redis-server
        elif command -v service &> /dev/null; then
            sudo service redis-server start
        else
            echo "❌ Cannot start Redis automatically, please start it manually"
            exit 1
        fi
    else
        echo "✅ Redis is running"
    fi
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade requirements
echo "📦 Installing requirements..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found, copying from example..."
    cp .env.example .env
    echo "❗ Please edit .env file with your credentials before running again"
    exit 1
fi

# Create necessary directories
mkdir -p data/logs data/tmp system

# Create system files if they don't exist
if [ ! -f "system/team" ]; then
    echo "YourTeamName" > system/team
fi

if [ ! -f "system/channel" ]; then
    echo "@YourChannel" > system/channel
fi

# Start the bot
echo "🚀 Starting bot..."
python3 start.py

# If bot exits, show message
echo "👋 Bot stopped"