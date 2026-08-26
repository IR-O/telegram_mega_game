from database.mongodb import db
from datetime import datetime
import random
import logging

logger = logging.getLogger(__name__)

class RacingGame:
    @staticmethod
    async def initialize_player(user_id: int) -> dict:
        """Initialize racing game player data"""
        racing_data = {
            'user_id': user_id,
            'level': 1,
            'xp': 0,
            'rating': 1000,
            'wins': 0,
            'losses': 0,
            'car': {
                'name': 'Civic',
                'speed': 50,
                'acceleration': 40,
                'handling': 60,
                'nitro': 30,
                'durability': 70
            },
            'garage': [],
            'upgrades': {'engine': 0, 'tires': 0, 'aero': 0, 'nitro': 0},
            'crew': None,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        await db.insert_one('racing_players', racing_data)
        return racing_data
    
    @staticmethod
    async def get_player(user_id: int) -> dict:
        """Get racing player data"""
        player = await db.find_one('racing_players', {'user_id': user_id})
        if not player:
            player = await RacingGame.initialize_player(user_id)
        return player
    
    @staticmethod
    async def race(racer_id: int, opponent_id: int) -> dict:
        """Race against another player"""
        racer = await RacingGame.get_player(racer_id)
        opponent = await RacingGame.get_player(opponent_id)
        
        # Calculate race
        racer_speed = racer['car']['speed'] + racer['upgrades']['engine'] * 2
        opponent_speed = opponent['car']['speed'] + opponent['upgrades']['engine'] * 2
        
        racer_acceleration = racer['car']['acceleration'] + racer['upgrades']['tires'] * 1.5
        opponent_acceleration = opponent['car']['acceleration'] + opponent['upgrades']['tires'] * 1.5
        
        racer_handling = racer['car']['handling'] + racer['upgrades']['aero'] * 1.5
        opponent_handling = opponent['car']['handling'] + opponent['upgrades']['aero'] * 1.5
        
        racer_nitro = racer['car']['nitro'] + racer['upgrades']['nitro'] * 3
        opponent_nitro = opponent['car']['nitro'] + opponent['upgrades']['nitro'] * 3
        
        # Simulate race
        racer_score = racer_speed * 0.4 + racer_acceleration * 0.3 + racer_handling * 0.2 + racer_nitro * 0.1
        opponent_score = opponent_speed * 0.4 + opponent_acceleration * 0.3 + opponent_handling * 0.2 + opponent_nitro * 0.1
        
        # Add random factor
        racer_random = random.uniform(0.8, 1.2)
        opponent_random = random.uniform(0.8, 1.2)
        
        racer_total = racer_score * racer_random
        opponent_total = opponent_score * opponent_random
        
        if racer_total > opponent_total:
            # Racer wins
            reward = random.randint(30, 80)
            xp_reward = random.randint(20, 40)
            
            await db.update_one(
                'racing_players',
                {'user_id': racer_id},
                {
                    '$inc': {
                        'wins': 1,
                        'xp': xp_reward,
                        'rating': 10
                    },
                    '$set': {'updated_at': datetime.utcnow()}
                }
            )
            
            return {
                'winner': racer_id,
                'winner_name': 'Racer',
                'reward': reward,
                'xp_reward': xp_reward,
                'message': f'🏁 Race Won!\n'
                           f'+{reward} coins, +{xp_reward} XP'
            }
        else:
            # Opponent wins
            await db.update_one(
                'racing_players',
                {'user_id': racer_id},
                {
                    '$inc': {
                        'losses': 1,
                        'rating': -5
                    },
                    '$set': {'updated_at': datetime.utcnow()}
                }
            )
            
            return {
                'winner': opponent_id,
                'winner_name': 'Opponent',
                'message': f'🏁 Race Lost!\n'
                           f'Better luck next time!'
            }
