from database.mongodb import db
from datetime import datetime
import random
import logging

logger = logging.getLogger(__name__)

class DetectiveGame:
    @staticmethod
    async def initialize_player(user_id: int) -> dict:
        """Initialize detective game player data"""
        detective_data = {
            'user_id': user_id,
            'level': 1,
            'xp': 0,
            'rating': 1000,
            'cases_solved': 0,
            'cases_failed': 0,
            'active_case': None,
            'clues': [],
            'suspects': [],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        await db.insert_one('detective_games', detective_data)
        return detective_data
    
    @staticmethod
    async def get_player(user_id: int) -> dict:
        """Get detective player data"""
        player = await db.find_one('detective_games', {'user_id': user_id})
        if not player:
            player = await DetectiveGame.initialize_player(user_id)
        return player
    
    @staticmethod
    async def new_case(user_id: int) -> dict:
        """Start a new mystery case"""
        player = await DetectiveGame.get_player(user_id)
        
        # Generate case
        suspects = ['Elena', 'Marcus', 'Sophia', 'James', 'Victoria', 'Oliver', 'Isabella', 'Lucas']
        locations = ['Mansion', 'Hotel', 'Office', 'Apartment', 'Studio', 'Library', 'Theater', 'Gallery']
        weapons = ['Knife', 'Gun', 'Poison', 'Rope', 'Hammer', 'Candlestick', 'Poisin', 'Firearm']
        
        killer = random.choice(suspects)
        location = random.choice(locations)
        weapon = random.choice(weapons)
        
        case = {
            'id': f"case_{datetime.utcnow().timestamp()}",
            'title': f'🔎 Murder at {location}',
            'killer': killer,
            'location': location,
            'weapon': weapon,
            'suspects': suspects.copy(),
            'clues_generated': False,
            'solved': False,
            'created_at': datetime.utcnow()
        }
        
        # Generate clues (3-5 clues)
        num_clues = random.randint(3, 5)
        clues = []
        for i in range(num_clues):
            clue_types = [
                f'Found {weapon} at {location}',
                f'Witness saw {killer} at {location}',
                f'Footprints found at {location}',
                f'CCTV footage of {killer} leaving',
                f'Phone records show {killer} called victim',
                f'Blood type matches {killer}',
                f'Fingerprints found on {weapon}'
            ]
            clue = random.choice(clue_types)
            if clue not in clues:
                clues.append(clue)
        
        case['clues'] = clues
        
        # Save case
        await db.update_one(
            'detective_games',
            {'user_id': user_id},
            {
                '$set': {
                    'active_case': case,
                    'clues': clues,
                    'suspects': suspects,
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        return {
            'case': case['title'],
            'suspects': suspects,
            'clues': clues,
            'message': f'📋 New Case: {case["title"]}\n\n'
                       f'Suspects: {", ".join(suspects[:5])}\n'
                       f'Clues found: {len(clues)}'
        }
    
    @staticmethod
    async def solve_case(user_id: int, suspect: str) -> dict:
        """Solve the case by accusing a suspect"""
        player = await DetectiveGame.get_player(user_id)
        
        case = player.get('active_case')
        if not case:
            return {'error': 'No active case!'}
        
        if case.get('solved', False):
            return {'error': 'Case already solved!'}
        
        # Check accusation
        if suspect == case['killer']:
            # Solved!
            reward = random.randint(50, 150) * (1 + player['level'] * 0.1)
            xp_reward = random.randint(30, 60)
            
            await db.update_one(
                'detective_games',
                {'user_id': user_id},
                {
                    '$inc': {
                        'cases_solved': 1,
                        'rating': 25,
                        'xp': int(xp_reward)
                    },
                    '$set': {
                        'active_case.solved': True,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            return {
                'result': 'solved',
                'suspect': suspect,
                'killer': case['killer'],
                'weapon': case['weapon'],
                'reward': int(reward),
                'xp_reward': int(xp_reward),
                'message': f'✅ Case Solved!\n'
                           f'{suspect} was the killer!\n'
                           f'Weapon: {case["weapon"]}\n'
                           f'+{int(reward)} coins, +{int(xp_reward)} XP'
            }
        else:
            # Wrong accusation
            await db.update_one(
                'detective_games',
                {'user_id': user_id},
                {
                    '$inc': {
                        'cases_failed': 1,
                        'rating': -10
                    },
                    '$set': {
                        'active_case.solved': True,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            return {
                'result': 'failed',
                'suspect': suspect,
                'killer': case['killer'],
                'message': f'❌ Wrong!\n'
                           f'{suspect} is not the killer.\n'
                           f'The real killer was {case["killer"]}.'
            }
