from database.mongodb import db
from datetime import datetime, timedelta
import random
import logging

logger = logging.getLogger(__name__)

class MindWarsGame:
    @staticmethod
    async def initialize_player(user_id: int) -> dict:
        """Initialize mind wars player data"""
        mind_data = {
            'user_id': user_id,
            'level': 1,
            'xp': 0,
            'rating': 1000,
            'wins': 0,
            'losses': 0,
            'daily_challenges': 0,
            'tournaments_won': 0,
            'games_played': 0,
            'best_streak': 0,
            'current_streak': 0,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        await db.insert_one('mind_wars', mind_data)
        return mind_data
    
    @staticmethod
    async def get_player(user_id: int) -> dict:
        """Get mind wars player data"""
        player = await db.find_one('mind_wars', {'user_id': user_id})
        if not player:
            player = await MindWarsGame.initialize_player(user_id)
        return player
    
    @staticmethod
    async def play_memory_game(user_id: int) -> dict:
        """Play memory game"""
        player = await MindWarsGame.get_player(user_id)
        
        # Generate memory sequence
        sequence_length = min(3 + player['level'], 10)
        sequence = [random.randint(1, 9) for _ in range(sequence_length)]
        
        # Simulate player memory (for bot demonstration)
        # In reality, this would be interactive
        player_score = random.random()
        
        if player_score > 0.7:
            # Win
            reward = random.randint(10, 30) * (1 + player['level'] * 0.1)
            xp_reward = random.randint(15, 35)
            
            await db.update_one(
                'mind_wars',
                {'user_id': user_id},
                {
                    '$inc': {
                        'wins': 1,
                        'xp': xp_reward,
                        'games_played': 1,
                        'current_streak': 1,
                        'rating': 5
                    },
                    '$set': {'updated_at': datetime.utcnow()}
                }
            )
            
            # Check for best streak
            if player['current_streak'] + 1 > player['best_streak']:
                await db.update_one(
                    'mind_wars',
                    {'user_id': user_id},
                    {'$set': {'best_streak': player['current_streak'] + 1}}
                )
            
            return {
                'game': 'memory',
                'result': 'win',
                'reward': int(reward),
                'xp_reward': xp_reward,
                'sequence': sequence,
                'message': f'🧩 Memory Game: WIN! +{int(reward)} coins, +{xp_reward} XP'
            }
        else:
            # Loss
            await db.update_one(
                'mind_wars',
                {'user_id': user_id},
                {
                    '$inc': {
                        'losses': 1,
                        'games_played': 1,
                        'current_streak': -(player['current_streak'])
                    },
                    '$set': {'updated_at': datetime.utcnow()}
                }
            )
            
            return {
                'game': 'memory',
                'result': 'loss',
                'sequence': sequence,
                'message': f'🧩 Memory Game: LOSS! Try again!'
            }
    
    @staticmethod
    async def play_math_game(user_id: int) -> dict:
        """Play math game"""
        player = await MindWarsGame.get_player(user_id)
        
        # Generate math problem
        operations = ['+', '-', '*']
        op = random.choice(operations)
        
        if op == '+':
            a = random.randint(1, 100)
            b = random.randint(1, 100)
            answer = a + b
        elif op == '-':
            a = random.randint(50, 100)
            b = random.randint(1, a)
            answer = a - b
        else:  # *
            a = random.randint(1, 12)
            b = random.randint(1, 12)
            answer = a * b
        
        # Simulate player answer (for bot demonstration)
        player_correct = random.random()
        
        if player_correct > 0.6:
            # Win
            reward = random.randint(15, 35) * (1 + player['level'] * 0.1)
            xp_reward = random.randint(20, 40)
            
            await db.update_one(
                'mind_wars',
                {'user_id': user_id},
                {
                    '$inc': {
                        'wins': 1,
                        'xp': xp_reward,
                        'games_played': 1,
                        'current_streak': 1,
                        'rating': 8
                    },
                    '$set': {'updated_at': datetime.utcnow()}
                }
            )
            
            return {
                'game': 'math',
                'result': 'win',
                'problem': f'{a} {op} {b} = ?',
                'answer': answer,
                'reward': int(reward),
                'xp_reward': xp_reward,
                'message': f'➗ Math Game: WIN! +{int(reward)} coins, +{xp_reward} XP'
            }
        else:
            # Loss
            await db.update_one(
                'mind_wars',
                {'user_id': user_id},
                {
                    '$inc': {
                        'losses': 1,
                        'games_played': 1,
                        'current_streak': -(player['current_streak'])
                    },
                    '$set': {'updated_at': datetime.utcnow()}
                }
            )
            
            return {
                'game': 'math',
                'result': 'loss',
                'problem': f'{a} {op} {b} = ?',
                'answer': answer,
                'message': f'➗ Math Game: LOSS! Try again!'
            }
