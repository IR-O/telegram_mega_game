import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    MONGO_DB_URI = os.getenv('MONGO_DB_URI')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'telegram_mega_game')
    ADMIN_IDS = [int(id.strip()) for id in os.getenv('ADMIN_IDS', '').split(',') if id.strip()]
    LOG_CHANNEL_ID = int(os.getenv('LOG_CHANNEL_ID', 0)) if os.getenv('LOG_CHANNEL_ID') else None
    
    # Game configurations
    MAX_DAILY_STREAK = 30
    ENERGY_RECHARGE_TIME = 300  # 5 minutes
    MAX_ENERGY = 100
    DAILY_BONUS_COINS = 1000
    DAILY_BONUS_XP = 100
    
    # Battle configurations
    BATTLE_COOLDOWN = 60  # seconds
    ROB_COOLDOWN = 300  # 5 minutes
    GANG_WAR_COOLDOWN = 3600  # 1 hour
    
    # Economy limits
    MAX_COINS = 10**9
    MAX_GEMS = 10**6
    
    # MongoDB indexes
    INDEXES = {
        'users': ['telegram_id', 'username', 'level'],
        'transactions': ['user_id', 'timestamp', 'type'],
        'battles': ['winner_id', 'loser_id', 'timestamp'],
        'gangs': ['gang_id', 'level', 'power'],
        'group_worlds': ['group_id', 'threat_level'],
        'global_events': ['active', 'end_time'],
    }
