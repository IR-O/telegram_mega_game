from database.mongodb import db
from datetime import datetime
import random
import logging

logger = logging.getLogger(__name__)

class DragonGame:
    @staticmethod
    async def initialize_player(user_id: int) -> dict:
        """Initialize dragon game player data"""
        dragon_data = {
            'user_id': user_id,
            'level': 1,
            'xp': 0,
            'kingdom_level': 1,
            'dragons': [],
            'eggs': 1,
            'resources': 100,
            'elements': {
                'fire': 0,
                'ice': 0,
                'lightning': 0,
                'water': 0,
                'nature': 0,
                'dark': 0,
                'light': 0
            },
            'battles_won': 0,
            'battles_lost': 0,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        await db.insert_one('dragons', dragon_data)
        return dragon_data
    
    @staticmethod
    async def get_player(user_id: int) -> dict:
        """Get dragon player data"""
        player = await db.find_one('dragons', {'user_id': user_id})
        if not player:
            player = await DragonGame.initialize_player(user_id)
        return player
    
    @staticmethod
    async def hatch_egg(user_id: int) -> dict:
        """Hatch a dragon egg"""
        player = await DragonGame.get_player(user_id)
        
        if player['eggs'] < 1:
            return {'error': 'No eggs to hatch!'}
        
        # Dragon types
        dragon_types = [
            {'name': 'Fire Dragon', 'element': 'fire', 'rarity': 'Common', 
             'hp': 50, 'attack': 15, 'defense': 10, 'speed': 8},
            {'name': 'Ice Dragon', 'element': 'ice', 'rarity': 'Common',
             'hp': 45, 'attack': 12, 'defense': 15, 'speed': 7},
            {'name': 'Lightning Dragon', 'element': 'lightning', 'rarity': 'Rare',
             'hp': 40, 'attack': 20, 'defense': 8, 'speed': 15},
            {'name': 'Water Dragon', 'element': 'water', 'rarity': 'Common',
             'hp': 55, 'attack': 10, 'defense': 12, 'speed': 6},
            {'name': 'Nature Dragon', 'element': 'nature', 'rarity': 'Rare',
             'hp': 50, 'attack': 14, 'defense': 14, 'speed': 9},
            {'name': 'Dark Dragon', 'element': 'dark', 'rarity': 'Epic',
             'hp': 60, 'attack': 18, 'defense': 12, 'speed': 10},
            {'name': 'Light Dragon', 'element': 'light', 'rarity': 'Epic',
             'hp': 55, 'attack': 16, 'defense': 16, 'speed': 11},
            {'name': 'Inferno Dragon', 'element': 'fire', 'rarity': 'Legendary',
             'hp': 80, 'attack': 25, 'defense': 15, 'speed': 12},
            {'name': 'Frost Dragon', 'element': 'ice', 'rarity': 'Legendary',
             'hp': 75, 'attack': 20, 'defense': 20, 'speed': 10}
        ]
        
        dragon = random.choice(dragon_types)
        
        new_dragon = {
            'id': f"dragon_{datetime.utcnow().timestamp()}",
            'name': dragon['name'],
            'element': dragon['element'],
            'rarity': dragon['rarity'],
            'hp': dragon['hp'],
            'max_hp': dragon['hp'],
            'attack': dragon['attack'],
            'defense': dragon['defense'],
            'speed': dragon['speed'],
            'level': 1,
            'xp': 0
        }
        
        await db.update_one(
            'dragons',
            {'user_id': user_id},
            {
                '$push': {'dragons': new_dragon},
                '$inc': {
                    'eggs': -1,
                    f'elements.{dragon["element"]}': 1,
                    'xp': random.randint(10, 30)
                },
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
        
        return {
            'dragon': dragon['name'],
            'element': dragon['element'],
            'rarity': dragon['rarity'],
            'stats': {
                'hp': dragon['hp'],
                'attack': dragon['attack'],
                'defense': dragon['defense'],
                'speed': dragon['speed']
            },
            'message': f'🥚 Hatched {dragon["rarity"]} {dragon["name"]}!'
        }
    
    @staticmethod
    async def train_dragon(user_id: int, dragon_id: str) -> dict:
        """Train a dragon"""
        player = await DragonGame.get_player(user_id)
        
        # Find dragon
        dragon = None
        dragon_index = -1
        for i, d in enumerate(player['dragons']):
            if d['id'] == dragon_id:
                dragon = d
                dragon_index = i
                break
        
        if not dragon:
            return {'error': 'Dragon not found!'}
        
        # Training cost
        if player['resources'] < 20:
            return {'error': 'Need 20 resources to train!'}
        
        # Training results
        hp_gain = random.randint(1, 5)
        attack_gain = random.randint(1, 3)
        defense_gain = random.randint(1, 3)
        speed_gain = random.randint(0, 2)
        
        # Update dragon
        updated_dragon = dragon.copy()
        updated_dragon['hp'] += hp_gain
        updated_dragon['max_hp'] += hp_gain
        updated_dragon['attack'] += attack_gain
        updated_dragon['defense'] += defense_gain
        updated_dragon['speed'] += speed_gain
        updated_dragon['level'] += 1
        
        # Remove old dragon and add updated
        await db.update_one(
            'dragons',
            {'user_id': user_id},
            {
                '$pull': {'dragons': {'id': dragon_id}},
                '$push': {'dragons': updated_dragon},
                '$inc': {
                    'resources': -20,
                    'xp': random.randint(5, 15)
                },
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
        
        return {
            'dragon': dragon['name'],
            'new_level': updated_dragon['level'],
            'hp_gain': hp_gain,
            'attack_gain': attack_gain,
            'defense_gain': defense_gain,
            'speed_gain': speed_gain,
            'message': f'⚔️ {dragon["name"]} trained to level {updated_dragon["level"]}!'
        }
