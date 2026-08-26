from database.mongodb import db
from datetime import datetime, timedelta
import random
import logging

logger = logging.getLogger(__name__)

class SpyGame:
    @staticmethod
    async def initialize_player(user_id: int) -> dict:
        """Initialize spy game player data"""
        spy_data = {
            'user_id': user_id,
            'level': 1,
            'xp': 0,
            'reputation': 0,
            'intelligence': 0,
            'equipment': [],
            'missions_completed': 0,
            'missions_failed': 0,
            'current_mission': None,
            'cooldown': None,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        await db.insert_one('spies', spy_data)
        return spy_data
    
    @staticmethod
    async def get_player(user_id: int) -> dict:
        """Get spy player data"""
        player = await db.find_one('spies', {'user_id': user_id})
        if not player:
            player = await SpyGame.initialize_player(user_id)
        return player
    
    @staticmethod
    async def get_mission(user_id: int) -> dict:
        """Get a new spy mission"""
        player = await SpyGame.get_player(user_id)
        
        # Check cooldown
        if player.get('cooldown') and datetime.utcnow() < player['cooldown']:
            remaining = (player['cooldown'] - datetime.utcnow()).seconds
            return {'error': f'⏰ Wait {remaining}s for next mission.'}
        
        missions = [
            {
                'name': 'Steal Documents',
                'difficulty': 'Easy',
                'success_chance': 0.8,
                'reward': 50,
                'xp': 20
            },
            {
                'name': 'Infiltrate Base',
                'difficulty': 'Medium',
                'success_chance': 0.6,
                'reward': 100,
                'xp': 40
            },
            {
                'name': 'Assassinate Target',
                'difficulty': 'Hard',
                'success_chance': 0.4,
                'reward': 200,
                'xp': 80
            },
            {
                'name': 'Steal Technology',
                'difficulty': 'Very Hard',
                'success_chance': 0.3,
                'reward': 300,
                'xp': 120
            },
            {
                'name': 'Double Agent',
                'difficulty': 'Extreme',
                'success_chance': 0.2,
                'reward': 500,
                'xp': 200
            }
        ]
        
        mission = random.choice(missions)
        
        # Apply level bonus
        level_bonus = player['level'] * 0.02
        success_chance = min(0.95, mission['success_chance'] + level_bonus)
        
        # Save mission
        await db.update_one(
            'spies',
            {'user_id': user_id},
            {
                '$set': {
                    'current_mission': mission,
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        return {
            'mission': mission['name'],
            'difficulty': mission['difficulty'],
            'success_chance': int(success_chance * 100),
            'reward': mission['reward'],
            'xp': mission['xp'],
            'message': f'📋 New Mission: {mission["name"]}\n'
                       f'Difficulty: {mission["difficulty"]}\n'
                       f'Success Chance: {int(success_chance * 100)}%\n'
                       f'Reward: {mission["reward"]} coins, {mission["xp"]} XP'
        }
    
    @staticmethod
    async def execute_mission(user_id: int) -> dict:
        """Execute the current spy mission"""
        player = await SpyGame.get_player(user_id)
        
        mission = player.get('current_mission')
        if not mission:
            return {'error': 'No active mission. Use /missions to get one.'}
        
        # Calculate success
        level_bonus = player['level'] * 0.02
        success_chance = min(0.95, mission['success_chance'] + level_bonus)
        
        # Equipment bonus
        equipment_bonus = len(player.get('equipment', [])) * 0.05
        success_chance = min(0.98, success_chance + equipment_bonus)
        
        if random.random() < success_chance:
            # Success
            reward = mission['reward'] * (1 + player['level'] * 0.1)
            xp_reward = mission['xp'] * (1 + player['level'] * 0.1)
            reputation_gain = random.randint(1, 5)
            
            # Intelligence gain
            intelligence_gain = random.randint(1, 10)
            
            await db.update_one(
                'spies',
                {'user_id': user_id},
                {
                    '$inc': {
                        'missions_completed': 1,
                        'reputation': reputation_gain,
                        'intelligence': intelligence_gain,
                        'xp': int(xp_reward)
                    },
                    '$set': {
                        'current_mission': None,
                        'cooldown': datetime.utcnow() + timedelta(minutes=5),
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            return {
                'result': 'success',
                'mission': mission['name'],
                'reward': int(reward),
                'xp_reward': int(xp_reward),
                'reputation_gain': reputation_gain,
                'intelligence_gain': intelligence_gain,
                'message': f'✅ Mission Successful!\n'
                           f'+{int(reward)} coins, +{int(xp_reward)} XP\n'
                           f'+{reputation_gain} reputation, +{intelligence_gain} intelligence'
            }
        else:
            # Failure
            reputation_loss = random.randint(1, 3)
            
            await db.update_one(
                'spies',
                {'user_id': user_id},
                {
                    '$inc': {
                        'missions_failed': 1,
                        'reputation': -reputation_loss
                    },
                    '$set': {
                        'current_mission': None,
                        'cooldown': datetime.utcnow() + timedelta(minutes=10),
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            return {
                'result': 'failed',
                'mission': mission['name'],
                'reputation_loss': reputation_loss,
                'message': f'❌ Mission Failed!\n'
                           f'Lost {reputation_loss} reputation.'
            }
