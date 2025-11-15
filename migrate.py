#!/usr/bin/env python3
"""
Migration script to help transfer data from the old Lua bot to the new Python bot
"""

import json
import os
import redis
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_from_lua_data():
    """Migrate data from old Lua bot format"""
    logger.info("🔄 Starting migration from Lua bot...")
    
    # Connect to Redis
    try:
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        r.ping()
        logger.info("✅ Connected to Redis")
    except Exception as e:
        logger.error(f"❌ Failed to connect to Redis: {e}")
        return False
    
    # Migrate moderation data if it exists
    moderation_file = Path("data/moderation.json")
    if moderation_file.exists():
        logger.info("📄 Found moderation data file, migrating...")
        try:
            with open(moderation_file, 'r') as f:
                data = json.load(f)
            
            # Save to Redis
            r.set("moderation:data", json.dumps(data))
            logger.info("✅ Moderation data migrated")
        except Exception as e:
            logger.error(f"❌ Failed to migrate moderation data: {e}")
    
    # Migrate other data files
    data_files = {
        "banned.json": "migrate_banned_users",
        "whitelist.json": "migrate_whitelist", 
        "sudo.json": "migrate_sudo_users",
        "settings.json": "migrate_settings"
    }
    
    for filename, migrate_func in data_files.items():
        filepath = Path("data") / filename
        if filepath.exists():
            logger.info(f"📄 Found {filename}, migrating...")
            try:
                globals()[migrate_func](filepath, r)
                logger.info(f"✅ {filename} migrated")
            except Exception as e:
                logger.error(f"❌ Failed to migrate {filename}: {e}")
    
    logger.info("🎉 Migration completed!")
    return True

def migrate_banned_users(filepath, redis_client):
    """Migrate banned users data"""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    # Migrate banned users
    for user_id, chat_data in data.get('banned', {}).items():
        for chat_id, admin_id in chat_data.items():
            redis_client.set(f"banned:{user_id}:{chat_id}", admin_id)
    
    # Migrate global bans
    if 'gbanned' in data:
        for user_id in data['gbanned']:
            redis_client.sadd("gbanned", user_id)

def migrate_whitelist(filepath, redis_client):
    """Migrate whitelist data"""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    for user_id in data.get('whitelist', []):
        redis_client.sadd("whitelist", user_id)

def migrate_sudo_users(filepath, redis_client):
    """Migrate sudo users data"""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    # Note: Sudo users are now configured via environment variables
    # This just logs the found sudo users for manual configuration
    sudo_users = data.get('sudo', [])
    if sudo_users:
        logger.info(f"ℹ️  Found sudo users: {sudo_users}")
        logger.info("ℹ️  Please add them to SUDO_USERS in your .env file")

def migrate_settings(filepath, redis_client):
    """Migrate chat settings"""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    for chat_id, settings in data.items():
        if isinstance(settings, dict):
            for setting, value in settings.items():
                redis_client.hset(f"chat:{chat_id}:settings", setting, str(value))

def create_backup():
    """Create backup of current Redis data"""
    logger.info("💾 Creating backup of current Redis data...")
    
    try:
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        
        # Get all keys
        keys = r.keys('*')
        backup_data = {}
        
        for key in keys:
            key_type = r.type(key)
            if key_type == 'string':
                backup_data[key] = {'type': 'string', 'value': r.get(key)}
            elif key_type == 'set':
                backup_data[key] = {'type': 'set', 'value': list(r.smembers(key))}
            elif key_type == 'hash':
                backup_data[key] = {'type': 'hash', 'value': r.hgetall(key)}
            elif key_type == 'list':
                backup_data[key] = {'type': 'list', 'value': r.lrange(key, 0, -1)}
        
        # Save backup
        backup_file = Path("data") / "redis_backup.json"
        backup_file.parent.mkdir(exist_ok=True)
        
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        logger.info(f"✅ Backup saved to {backup_file}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create backup: {e}")
        return False

def restore_backup(backup_file):
    """Restore Redis data from backup"""
    logger.info(f"🔄 Restoring from backup: {backup_file}")
    
    try:
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        
        with open(backup_file, 'r') as f:
            backup_data = json.load(f)
        
        for key, data in backup_data.items():
            if data['type'] == 'string':
                r.set(key, data['value'])
            elif data['type'] == 'set':
                r.delete(key)
                for value in data['value']:
                    r.sadd(key, value)
            elif data['type'] == 'hash':
                r.delete(key)
                if data['value']:
                    r.hset(key, mapping=data['value'])
            elif data['type'] == 'list':
                r.delete(key)
                for value in data['value']:
                    r.rpush(key, value)
        
        logger.info("✅ Backup restored successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to restore backup: {e}")
        return False

def main():
    """Main migration function"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 migrate.py <command>")
        print("Commands:")
        print("  migrate    - Migrate from old Lua bot data")
        print("  backup     - Create backup of current Redis data")
        print("  restore    - Restore from backup file")
        return
    
    command = sys.argv[1]
    
    if command == "migrate":
        migrate_from_lua_data()
    elif command == "backup":
        create_backup()
    elif command == "restore":
        if len(sys.argv) < 3:
            print("Usage: python3 migrate.py restore <backup_file>")
            return
        restore_backup(sys.argv[2])
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()