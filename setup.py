#!/usr/bin/env python3
"""
Setup script for Modern Telegram Bot
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path

def check_python():
    """Check Python version"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def install_requirements():
    """Install Python requirements"""
    print("📦 Installing Python requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements")
        sys.exit(1)

def setup_storage():
    """Setup data storage"""
    print("🔧 Setting up data storage...")
    
    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Create data file if it doesn't exist
    data_file = data_dir / "bot_data.json"
    if not data_file.exists():
        initial_data = {
            'users': {},
            'banned': {},
            'gbanned': [],
            'whitelist': [],
            'chat_users': {},
            'user_msgs': {},
            'spam_count': {},
            'chat_settings': {},
            'help_texts': {},
            'languages': {},
            'bot_settings': {},
            'user_chat_msgs': {}
        }
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, indent=2)
        print("✅ Created initial data file")
    else:
        print("✅ Data file already exists")
    
    print("✅ File-based storage ready")

def create_config():
    """Create configuration files"""
    print("⚙️  Creating configuration files...")
    
    # Copy .env example if .env doesn't exist
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            shutil.copy(".env.example", ".env")
            print("✅ Created .env from example")
            print("❗ Please edit .env file with your credentials")
        else:
            print("❌ .env.example not found")
    else:
        print("ℹ️  .env file already exists")
    
    # Create directories
    dirs = ["data", "data/logs", "data/tmp", "system"]
    for dir_path in dirs:
        Path(dir_path).mkdir(exist_ok=True)
    print("✅ Created necessary directories")
    
    # Create system files
    system_files = {
        "system/team": "YourTeamName",
        "system/channel": "@YourChannel"
    }
    
    for file_path, content in system_files.items():
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                f.write(content)
            print(f"✅ Created {file_path}")

def setup_systemd():
    """Setup systemd service (optional)"""
    print("🔧 Setting up systemd service...")
    
    service_content = f"""[Unit]
Description=Modern Telegram Bot
After=network.target redis.service

[Service]
Type=simple
User={os.getenv('USER', 'telegram')}
WorkingDirectory={os.getcwd()}
ExecStart={sys.executable} start.py
Restart=always
RestartSec=10
Environment=PYTHONPATH={os.getcwd()}

[Install]
WantedBy=multi-user.target
"""
    
    service_file = "/etc/systemd/system/telegram-bot.service"
    
    try:
        with open("telegram-bot.service", "w") as f:
            f.write(service_content)
        
        print(f"✅ Created service file: telegram-bot.service")
        print("To install the service, run:")
        print(f"  sudo cp telegram-bot.service {service_file}")
        print("  sudo systemctl daemon-reload")
        print("  sudo systemctl enable telegram-bot")
        print("  sudo systemctl start telegram-bot")
        
    except Exception as e:
        print(f"⚠️  Could not create service file: {e}")

def main():
    """Main setup function"""
    print("🤖 Setting up Modern Telegram Bot...")
    print("=" * 50)
    
    check_python()
    install_requirements()
    setup_storage()
    create_config()
    
    # Ask about systemd service
    if sys.platform.startswith('linux'):
        response = input("Do you want to create a systemd service? (y/N): ")
        if response.lower() in ['y', 'yes']:
            setup_systemd()
    
    print("\n🎉 Setup completed!")
    print("\n📝 Next steps:")
    print("1. Edit .env file with your Telegram credentials")
    print("2. Make sure Redis is running")
    print("3. Run: python3 start.py")
    print("\n📚 For more information, see README_NEW.md")

if __name__ == "__main__":
    main()