from database.mongodb import db
from datetime import datetime, timedelta
import random
import logging

logger = logging.getLogger(__name__)

class SpaceGame:
    @staticmethod
    async def initialize_player(user_id: int) -> dict:
        """Initialize space empire player data"""
        space_data = {
            'user_id': user_id,
            'level': 1,
            'xp': 0,
            'fleet_power': 100,
            'planets': [
                {
                    'name': 'New Earth',
                    'level': 1,
                    'resources': {'ore': 100, 'crystals': 10, 'energy': 50},
                    'defense': 10,
                    'production': {'ore': 10, 'crystals': 1, 'energy': 5}
                }
            ],
            'fleet': {
                'ships': 1,
                'power': 100,
                'upgrades': {'weapons': 1, 'shields': 1, 'engines': 1}
            },
            'resources': {'ore': 100, 'crystals': 10, 'energy': 50},
            'explored': 0,
            'colonies': 0,
            'alliances': [],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        await db.insert_one('space_players', space_data)
        return space_data
    
    @staticmethod
    async def get_player(user_id: int) -> dict:
        """Get space player data"""
        player = await db.find_one('space_players', {'user_id': user_id})
        if not player:
            player = await SpaceGame.initialize_player(user_id)
        return player
    
    @staticmethod
    async def explore(user_id: int) -> dict:
        """Explore the galaxy"""
        player = await SpaceGame.get_player(user_id)
        
        # Exploration results
        discoveries = [
            {'type': 'planet', 'name': f'Planet {random.randint(1000, 9999)}', 'resources': random.randint(50, 200)},
            {'type': 'resources', 'amount': random.randint(10, 50)},
            {'type': 'alien_encounter', 'strength': random.randint(1, 10)},
            {'type': 'space_pirates', 'strength': random.randint(1, 5)},
            {'type': 'ancient_ruins', 'reward': random.randint(50, 150)}
        ]
        
        discovery = random.choice(discoveries)
        
        if discovery['type'] == 'planet':
            # Add new planet
            planet = {
                'name': discovery['name'],
                'level': 1,
                'resources': {'ore': discovery['resources'], 'crystals': discovery['resources'] // 10, 'energy': discovery['resources'] // 5},
                'defense': random.randint(5, 20),
                'production': {'ore': random.randint(5, 15), 'crystals': random.randint(1, 3), 'energy': random.randint(2, 8)}
            }
            player['planets'].append(planet)
            await db.update_one(
                'space_players',
                {'user_id': user_id},
                {
                    '$push': {'planets': planet},
                    '$inc': {
                        'xp': random.randint(20, 50),
                        'colonies': 1,
                        'explored': 1,
                        'resources.ore': discovery['resources'] // 2
                    },
                    '$set': {'updated_at': datetime.utcnow()}
                }
            )
            return {'type': 'planet', 'name': discovery['name'], 'resources': discovery['resources']}
        
        elif discovery['type'] == 'resources':
            # Found resources
            await db.update_one(
                'space_players',
                {'user_id': user_id},
                {
                    '$inc': {
                        f'resources.ore': discovery['amount'] * 2,
                        f'resources.crystals': discovery['amount'] // 5,
                        'xp': random.randint(10, 30),
                        'explored': 1
                    },
                    '$set': {'updated_at': datetime.utcnow()}
                }
            )
            return {'type': 'resources', 'amount': discovery['amount'] * 2}
        
        elif discovery['type'] == 'alien_encounter':
            # Alien encounter - battle or diplomacy
            diplomacy = random.choice(['fight', 'diplomacy'])
            if diplomacy == 'fight':
                # Battle
                if player['fleet_power'] > discovery['strength'] * 10:
                    reward = discovery['strength'] * 20
                    await db.update_one(
                        'space_players',
                        {'user_id': user_id},
                        {
                            '$inc': {
                                'xp': discovery['strength'] * 10,
                                'fleet_power': discovery['strength'] * 2,
                                'resources.ore': reward,
                                'explored': 1
                            },
                            '$set': {'updated_at': datetime.utcnow()}
                        }
                    )
                    return {'type': 'alien_encounter', 'result': 'victory', 'reward': reward}
                else:
                    # Defeat
                    damage = random.randint(10, 30)
                    await db.update_one(
                        'space_players',
                        {'user_id': user_id},
                        {
                            '$inc': {
                                'fleet_power': -damage,
                                'explored': 1
                            },
                            '$set': {'updated_at': datetime.utcnow()}
                        }
                    )
                    return {'type': 'alien_encounter', 'result': 'defeat', 'damage': damage}
            else:
                # Diplomacy
                await db.update_one(
                    'space_players',
                    {'user_id': user_id},
                    {
                        '$inc': {
                            'xp': random.randint(10, 25),
                            'resources.energy': discovery['strength'] * 10,
                            'explored': 1
                        },
                        '$set': {'updated_at': datetime.utcnow()}
                    }
                )
                return {'type': 'alien_encounter', 'result': 'diplomacy', 'energy_gained': discovery['strength'] * 10}
        
        else:
            # Other discoveries
            await db.update_one(
                'space_players',
                {'user_id': user_id},
                {
                    '$inc': {
                        'xp': random.randint(5, 20),
                        'resources.ore': discovery.get('reward', 0),
                        'explored': 1
                    },
                    '$set': {'updated_at': datetime.utcnow()}
                }
            )
            return {'type': discovery['type'], 'reward': discovery.get('reward', 0)}
    
    @staticmethod
    async def mine(user_id: int) -> dict:
        """Mine resources"""
        player = await SpaceGame.get_player(user_id)
        
        # Check energy
        if player['resources']['energy'] < 10:
            return {'error': 'Not enough energy! Need 10 energy to mine.'}
        
        # Mining results
        ore_mined = random.randint(10, 50)
        crystals_mined = random.randint(1, 5)
        energy_used = random.randint(5, 15)
        
        # Apply level bonus
        level_bonus = player.get('level', 1) * 2
        ore_mined += level_bonus
        
        await db.update_one(
            'space_players',
            {'user_id': user_id},
            {
                '$inc': {
                    'resources.ore': ore_mined,
                    'resources.crystals': crystals_mined,
                    'resources.energy': -energy_used,
                    'xp': random.randint(5, 15)
                },
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
        
        return {
            'ore_mined': ore_mined,
            'crystals_mined': crystals_mined,
            'energy_used': energy_used
        }
