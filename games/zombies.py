from database.mongodb import db
from datetime import datetime, timedelta
import random
import logging

logger = logging.getLogger(__name__)

class ZombieGame:
    @staticmethod
    async def initialize_player(user_id: int) -> dict:
        """Initialize zombie apocalypse player data"""
        zombie_data = {
            'user_id': user_id,
            'level': 1,
            'xp': 0,
            'health': 100,
            'max_health': 100,
            'food': 50,
            'water': 50,
            'weapon': None,
            'shelter': None,
            'zombies_killed': 0,
            'survivors_saved': 0,
            'location': 'safe_zone',
            'inventory': {'weapons': [], 'supplies': [], 'medicals': []},
            'stats': {'strength': 5, 'agility': 5, 'intelligence': 5},
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        await db.insert_one('zombie_players', zombie_data)
        return zombie_data
    
    @staticmethod
    async def get_player(user_id: int) -> dict:
        """Get zombie player data"""
        player = await db.find_one('zombie_players', {'user_id': user_id})
        if not player:
            player = await ZombieGame.initialize_player(user_id)
        return player
    
    @staticmethod
    async def fight_zombie(user_id: int) -> dict:
        """Fight zombies"""
        player = await ZombieGame.get_player(user_id)
        
        # Check health
        if player['health'] <= 0:
            return {'error': 'You are dead! Use /revive to come back.'}
        
        # Check food/water
        if player['food'] < 5 or player['water'] < 5:
            return {'error': 'Low on resources! Need food and water to fight.'}
        
        # Generate zombie
        zombie_types = [
            {'name': 'Walker', 'health': 20, 'damage': 5, 'reward': 10},
            {'name': 'Runner', 'health': 15, 'damage': 10, 'reward': 15},
            {'name': 'Tank', 'health': 50, 'damage': 15, 'reward': 30},
            {'name': 'Boomer', 'health': 30, 'damage': 20, 'reward': 25},
            {'name': 'Boss', 'health': 100, 'damage': 30, 'reward': 50}
        ]
        
        zombie = random.choice(zombie_types)
        
        # Apply difficulty based on level
        level_multiplier = player.get('level', 1)
        zombie_health = zombie['health'] + (level_multiplier - 1) * 10
        zombie_damage = zombie['damage'] + (level_multiplier - 1) * 2
        reward_multiplier = 1 + (level_multiplier - 1) * 0.1
        
        # Fight
        player_health = player['health']
        zombie_health_current = zombie_health
        
        rounds = 0
        while player_health > 0 and zombie_health_current > 0:
            rounds += 1
            # Player attacks
            damage = random.randint(5, 15) + player['stats'].get('strength', 5)
            zombie_health_current -= damage
            
            if zombie_health_current <= 0:
                break
            
            # Zombie attacks
            zombie_damage_dealt = random.randint(1, zombie_damage) - player['stats'].get('agility', 5) // 2
            if zombie_damage_dealt < 0:
                zombie_damage_dealt = 0
            player_health -= zombie_damage_dealt
        
        # Calculate rewards
        if zombie_health_current <= 0:
            # Victory
            reward_coins = int(zombie['reward'] * reward_multiplier)
            reward_xp = int((zombie['reward'] // 2) * reward_multiplier)
            reward_food = random.randint(5, 15)
            reward_water = random.randint(5, 15)
            
            # Check for item drops
            item_drop = random.random() < 0.2  # 20% chance
            item = None
            if item_drop:
                items = ['Pistol', 'Shotgun', 'Medical Kit', 'Ammo', 'Grenade']
                item = random.choice(items)
            
            # Update player
            await db.update_one(
                'zombie_players',
                {'user_id': user_id},
                {
                    '$inc': {
                        'health': -zombie_damage_dealt,
                        'food': -min(5, player['food']),
                        'water': -min(5, player['water']),
                        'xp': reward_xp,
                        'zombies_killed': 1
                    },
                    '$set': {'updated_at': datetime.utcnow()}
                }
            )
            
            # Add item to inventory
            if item:
                await db.update_one(
                    'zombie_players',
                    {'user_id': user_id},
                    {'$push': {'inventory.weapons': item}}
                )
            
            return {
                'result': 'victory',
                'zombie': zombie['name'],
                'rounds': rounds,
                'health_loss': zombie_damage_dealt,
                'reward_coins': reward_coins,
                'reward_xp': reward_xp,
                'item': item,
                'message': f'🧟 Defeated {zombie["name"]}! +{reward_coins} coins, +{reward_xp} XP'
            }
        else:
            # Defeat
            await db.update_one(
                'zombie_players',
                {'user_id': user_id},
                {
                    '$inc': {
                        'health': -zombie_damage_dealt,
                        'food': -min(5, player['food']),
                        'water': -min(5, player['water'])
                    },
                    '$set': {'updated_at': datetime.utcnow()}
                }
            )
            
            return {
                'result': 'defeat',
                'zombie': zombie['name'],
                'rounds': rounds,
                'health_loss': zombie_damage_dealt,
                'message': f'💀 Defeated by {zombie["name"]}! Lost {zombie_damage_dealt} HP'
            }
