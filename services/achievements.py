from database.mongodb import db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AchievementService:
    ACHIEVEMENTS = {
        'first_blood': {
            'id': 'first_blood',
            'name': 'First Blood',
            'description': 'Win your first battle',
            'condition': {'total_wins': {'$gte': 1}},
            'reward': {'coins': 100, 'xp': 50}
        },
        'millionaire': {
            'id': 'millionaire',
            'name': 'Millionaire',
            'description': 'Have 1,000,000 coins',
            'condition': {'coins': {'$gte': 1000000}},
            'reward': {'coins': 5000, 'xp': 1000, 'title': 'Millionaire'}
        },
        'battle_hundred': {
            'id': 'battle_hundred',
            'name': '100 Battles',
            'description': 'Fight in 100 battles',
            'condition': {'total_wins': {'$gte': 50}, 'games_played': {'$gte': 100}},
            'reward': {'coins': 1000, 'xp': 500, 'title': 'Warrior'}
        },
        'gang_leader': {
            'id': 'gang_leader',
            'name': 'Gang Leader',
            'description': 'Create and lead a gang',
            'condition': {'gang_rank': {'$eq': 'Boss'}},
            'reward': {'coins': 2000, 'xp': 1000, 'title': 'Gang Leader'}
        },
        'dragon_master': {
            'id': 'dragon_master',
            'name': 'Dragon Master',
            'description': 'Train 5 dragons',
            'condition': {'dragons_count': {'$gte': 5}},
            'reward': {'coins': 5000, 'xp': 2000, 'title': 'Dragon Master'}
        },
        'zombie_survivor': {
            'id': 'zombie_survivor',
            'name': 'Zombie Survivor',
            'description': 'Kill 100 zombies',
            'condition': {'zombies_killed': {'$gte': 100}},
            'reward': {'coins': 2000, 'xp': 1000, 'title': 'Survivor'}
        },
        'pirate_king': {
            'id': 'pirate_king',
            'name': 'Pirate King',
            'description': 'Capture 10 islands',
            'condition': {'islands_captured': {'$gte': 10}},
            'reward': {'coins': 3000, 'xp': 1500, 'title': 'Pirate King'}
        },
        'racing_champion': {
            'id': 'racing_champion',
            'name': 'Racing Champion',
            'description': 'Win 50 races',
            'condition': {'racing_wins': {'$gte': 50}},
            'reward': {'coins': 2000, 'xp': 1000, 'title': 'Racing Champion'}
        },
        'master_detective': {
            'id': 'master_detective',
            'name': 'Master Detective',
            'description': 'Solve 20 cases',
            'condition': {'cases_solved': {'$gte': 20}},
            'reward': {'coins': 3000, 'xp': 1500, 'title': 'Master Detective'}
        }
    }
    
    @staticmethod
    async def check_achievements(user_id: int):
        """Check and unlock achievements for a user"""
        user = await db.find_one('users', {'telegram_id': user_id})
        if not user:
            return []
        
        # Get user's unlocked achievements
        unlocked = await db.find('achievements', {'user_id': user_id})
        unlocked_ids = [a['achievement_id'] for a in unlocked]
        
        new_achievements = []
        
        for ach_id, achievement in AchievementService.ACHIEVEMENTS.items():
            if ach_id in unlocked_ids:
                continue
            
            # Check if user meets the condition
            condition_met = True
            for key, value in achievement['condition'].items():
                if key == '$gte':
                    # Handle MongoDB-like conditions
                    continue
                if user.get(key, 0) < value:
                    condition_met = False
                    break
            
            if condition_met:
                # Unlock achievement
                ach_data = {
                    'user_id': user_id,
                    'achievement_id': ach_id,
                    'name': achievement['name'],
                    'description': achievement['description'],
                    'unlocked_at': datetime.utcnow()
                }
                await db.insert_one('achievements', ach_data)
                
                # Apply rewards
                reward = achievement['reward']
                if 'coins' in reward:
                    from services.economy import EconomyService
                    await EconomyService.add_coins(
                        user_id,
                        reward['coins'],
                        f'Achievement: {achievement["name"]}'
                    )
                
                if 'title' in reward:
                    await db.update_one(
                        'users',
                        {'telegram_id': user_id},
                        {'$push': {'titles': reward['title']}}
                    )
                
                new_achievements.append(achievement)
        
        return new_achievements
