from database.mongodb import db
from datetime import datetime
import random
import logging

logger = logging.getLogger(__name__)

class MutationGame:
    @staticmethod
    async def initialize_player(user_id: int) -> dict:
        """Initialize mutation lab player data"""
        mutation_data = {
            'user_id': user_id,
            'level': 1,
            'xp': 0,
            'eggs': 3,
            'dna': 10,
            'creatures': [],
            'mutations': 0,
            'evolutions': 0,
            'battles_won': 0,
            'battles_lost': 0,
            'experiments': [],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        await db.insert_one('mutations', mutation_data)
        return mutation_data
    
    @staticmethod
    async def get_player(user_id: int) -> dict:
        """Get mutation player data"""
        player = await db.find_one('mutations', {'user_id': user_id})
        if not player:
            player = await MutationGame.initialize_player(user_id)
        return player
    
    @staticmethod
    async def collect(user_id: int) -> dict:
        """Collect resources"""
        player = await MutationGame.get_player(user_id)
        
        # Collect resources
        dna_collected = random.randint(1, 5)
        egg_chance = random.random() < 0.3
        
        await db.update_one(
            'mutations',
            {'user_id': user_id},
            {
                '$inc': {
                    'dna': dna_collected,
                    'eggs': 1 if egg_chance else 0,
                    'xp': random.randint(1, 5)
                },
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
        
        message = f'🧬 Collected {dna_collected} DNA!'
        if egg_chance:
            message += ' 🥚 Found an egg!'
        
        return {'dna': dna_collected, 'egg_found': egg_chance, 'message': message}
    
    @staticmethod
    async def breed(user_id: int) -> dict:
        """Breed creatures"""
        player = await MutationGame.get_player(user_id)
        
        if player['eggs'] < 2:
            return {'error': 'Need at least 2 eggs to breed!'}
        
        if player['dna'] < 5:
            return {'error': 'Need 5 DNA to breed!'}
        
        # Breed creatures
        creature_types = [
            {'name': 'Fire Dragon', 'rarity': 'Rare', 'attack': 20, 'defense': 10},
            {'name': 'Ice Wyrm', 'rarity': 'Rare', 'attack': 15, 'defense': 15},
            {'name': 'Thunder Bird', 'rarity': 'Epic', 'attack': 25, 'defense': 8},
            {'name': 'Shadow Wolf', 'rarity': 'Rare', 'attack': 18, 'defense': 12},
            {'name': 'Inferno Dragon', 'rarity': 'Legendary', 'attack': 35, 'defense': 20},
            {'name': 'Frost Giant', 'rarity': 'Epic', 'attack': 22, 'defense': 18},
            {'name': 'Storm Elemental', 'rarity': 'Legendary', 'attack': 30, 'defense': 15},
            {'name': 'Crystal Serpent', 'rarity': 'Rare', 'attack': 12, 'defense': 20}
        ]
        
        creature = random.choice(creature_types)
        
        # Check if creature already exists (can have duplicates)
        creature_id = f"{creature['name']}_{datetime.utcnow().timestamp()}"
        
        new_creature = {
            'id': creature_id,
            'name': creature['name'],
            'rarity': creature['rarity'],
            'attack': creature['attack'],
            'defense': creature['defense'],
            'level': 1,
            'xp': 0
        }
        
        await db.update_one(
            'mutations',
            {'user_id': user_id},
            {
                '$push': {'creatures': new_creature},
                '$inc': {
                    'eggs': -2,
                    'dna': -5,
                    'mutations': 1,
                    'xp': random.randint(10, 30)
                },
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
        
        return {
            'creature': creature['name'],
            'rarity': creature['rarity'],
            'attack': creature['attack'],
            'defense': creature['defense'],
            'message': f'🧬 Bred {creature["rarity"]} {creature["name"]}!'
        }
    
    @staticmethod
    async def evolve(user_id: int, creature_id: str) -> dict:
        """Evolve a creature"""
        player = await MutationGame.get_player(user_id)
        
        # Find creature
        creature = None
        for c in player['creatures']:
            if c['id'] == creature_id:
                creature = c
                break
        
        if not creature:
            return {'error': 'Creature not found!'}
        
        if player['dna'] < 10:
            return {'error': 'Need 10 DNA to evolve!'}
        
        # Evolution logic
        evolution_chance = 0.5 + creature['level'] * 0.05
        
        if random.random() < evolution_chance:
            # Successful evolution
            new_level = creature['level'] + 1
            attack_bonus = random.randint(1, 5)
            defense_bonus = random.randint(1, 5)
            
            # Update creature
            updated_creature = creature.copy()
            updated_creature['level'] = new_level
            updated_creature['attack'] += attack_bonus
            updated_creature['defense'] += defense_bonus
            
            # Remove old creature and add updated
            await db.update_one(
                'mutations',
                {'user_id': user_id},
                {
                    '$pull': {'creatures': {'id': creature_id}},
                    '$push': {'creatures': updated_creature},
                    '$inc': {
                        'dna': -10,
                        'evolutions': 1,
                        'xp': random.randint(20, 50)
                    },
                    '$set': {'updated_at': datetime.utcnow()}
                }
            )
            
            return {
                'result': 'success',
                'creature': creature['name'],
                'new_level': new_level,
                'attack_bonus': attack_bonus,
                'defense_bonus': defense_bonus,
                'message': f'⬆ {creature["name"]} evolved to level {new_level}!'
            }
        else:
            # Failed evolution
            await db.update_one(
                'mutations',
                {'user_id': user_id},
                {
                    '$inc': {'dna': -5},
                    '$set': {'updated_at': datetime.utcnow()}
                }
            )
            
            return {
                'result': 'failed',
                'creature': creature['name'],
                'message': f'❌ Evolution failed! Lost 5 DNA.'
            }
