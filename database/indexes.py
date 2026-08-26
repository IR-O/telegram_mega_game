from .mongodb import db

async def ensure_indexes():
    """Ensure all required indexes exist"""
    # Users
    await db.db.users.create_index('telegram_id', unique=True)
    await db.db.users.create_index([('level', -1)])
    await db.db.users.create_index([('coins', -1)])
    
    # Transactions
    await db.db.transactions.create_index([('user_id', 1), ('timestamp', -1)])
    
    # Battles
    await db.db.battles.create_index([('timestamp', -1)])
    await db.db.battles.create_index([('winner_id', 1), ('timestamp', -1)])
    
    # Gangs
    await db.db.gangs.create_index('gang_id', unique=True)
    await db.db.gangs.create_index([('power', -1)])
    
    # Group worlds
    await db.db.group_worlds.create_index('group_id', unique=True)
    
    # Global events
    await db.db.global_events.create_index([('active', 1), ('end_time', 1)])
    
    # Cooldowns
    await db.db.cooldowns.create_index([('user_id', 1), ('type', 1)], unique=True)
    await db.db.cooldowns.create_index('expires_at')
    
    # Achievements
    await db.db.achievements.create_index([('user_id', 1), ('achievement_id', 1)], unique=True)
