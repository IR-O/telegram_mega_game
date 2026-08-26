from database.mongodb import db
from datetime import datetime, timedelta
import random
import logging

logger = logging.getLogger(__name__)

class PirateGame:
    @staticmethod
    async def initialize_player(user_id: int) -> dict:
        """Initialize pirate empire player data"""
        pirate_data = {
            'user_id': user_id,
            'level': 1,
            'xp': 0,
            'ship': {
                'name': 'Sloop',
                'type': 'sloop',
                'attack': 10,
                'defense': 5,
                'speed': 8,
                'cargo': 50,
                'crew_capacity': 5,
                'crew': 5,
                'upgrades': {'cannons': 1, 'hull': 1, 'sails': 1}
            },
            'crew': 5,
            'gold': 100,
            'islands': [],
            'treasure': 0,
            'naval_battles_won': 0,
            'naval_battles_lost': 0,
            'inventory': {'weapons': [], 'supplies': [], 'treasure': []},
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        await db.insert_one('pirates', pirate_data)
        return pirate_data
    
    @staticmethod
    async def get_player(user_id: int) -> dict:
        """Get pirate player data"""
        player = await db.find_one('pirates', {'user_id': user_id})
        if not player:
            player = await PirateGame.initialize_player(user_id)
        return player
    
    @staticmethod
    async def sail(user_id: int) -> dict:
        """Set sail and explore"""
        player = await PirateGame.get_player(user_id)
        
        # Check crew
        if player['crew'] < 1:
            return {'error': 'No crew! Need at least 1 crew member to sail.'}
        
        # Random events while sailing
        events = [
            {'type': 'treasure', 'chance': 0.3},
            {'type': 'naval_battle', 'chance': 0.2},
            {'type': 'island', 'chance': 0.2},
            {'type': 'storm', 'chance': 0.15},
            {'type': 'merchant', 'chance': 0.15}
        ]
        
        # Weighted random selection
        total_chance = sum(e['chance'] for e in events)
        roll = random.random() * total_chance
        cumulative = 0
        
        selected_event = None
        for event in events:
            cumulative += event['chance']
            if roll <= cumulative:
                selected_event = event
                break
        
        if not selected_event:
            selected_event = events[0]
        
        # Handle event
        if selected_event['type'] == 'treasure':
            return await PirateGame._find_treasure(user_id)
        elif selected_event['type'] == 'naval_battle':
            return await PirateGame._naval_battle(user_id)
        elif selected_event['type'] == 'island':
            return await PirateGame._discover_island(user_id)
        elif selected_event['type'] == 'storm':
            return await PirateGame._survive_storm(user_id)
        elif selected_event['type'] == 'merchant':
            return await PirateGame._trade_with_merchant(user_id)
    
    @staticmethod
    async def _find_treasure(user_id: int) -> dict:
        """Find treasure while sailing"""
        player = await PirateGame.get_player(user_id)
        
        gold_found = random.randint(10, 100) * (player['level'] + 1)
        
        await db.update_one(
            'pirates',
            {'user_id': user_id},
            {
                '$inc': {
                    'gold': gold_found,
                    'treasure': gold_found // 2,
                    'xp': random.randint(5, 20)
                },
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
        
        return {
            'type': 'treasure',
            'gold_found': gold_found,
            'message': f'💰 Found treasure! +{gold_found} gold!'
        }
    
    @staticmethod
    async def _naval_battle(user_id: int) -> dict:
        """Engage in naval battle"""
        player = await PirateGame.get_player(user_id)
        
        # Generate enemy
        enemy_types = [
            {'name': 'Merchant Ship', 'attack': 5, 'defense': 3, 'gold': 50},
            {'name': 'Pirate Hunter', 'attack': 15, 'defense': 10, 'gold': 100},
            {'name': 'Naval Vessel', 'attack': 20, 'defense': 15, 'gold': 150},
            {'name': 'Treasure Galleon', 'attack': 10, 'defense': 8, 'gold': 200}
        ]
        
        enemy = random.choice(enemy_types)
        
        # Calculate battle
        player_attack = player['ship']['attack'] + player['ship']['upgrades']['cannons'] * 2
        player_defense = player['ship']['defense'] + player['ship']['upgrades']['hull'] * 2
        
        enemy_attack = enemy['attack'] * (1 + random.random() * 0.2)
        enemy_defense = enemy['defense'] * (1 + random.random() * 0.2)
        
        # Simulate battle
        player_hp = 100
        enemy_hp = 100
        
        rounds = 0
        while player_hp > 0 and enemy_hp > 0:
            rounds += 1
            # Player attacks
            damage = max(1, player_attack - enemy_defense // 2 + random.randint(-5, 10))
            enemy_hp -= damage
            
            if enemy_hp <= 0:
                break
            
            # Enemy attacks
            damage = max(1, enemy_attack - player_defense // 2 + random.randint(-5, 10))
            player_hp -= damage
        
        if enemy_hp <= 0:
            # Victory
            gold_reward = enemy['gold'] * (1 + random.random() * 0.5)
            xp_reward = random.randint(20, 50)
            
            # Chance of loot
            loot_chance = random.random()
            loot = None
            if loot_chance < 0.1:
                loot = 'Rare Cannon'
            elif loot_chance < 0.2:
                loot = 'Treasure Map'
            
            await db.update_one(
                'pirates',
                {'user_id': user_id},
                {
                    '$inc': {
                        'gold': int(gold_reward),
                        'xp': xp_reward,
                        'naval_battles_won': 1
                    },
                    '$set': {'updated_at': datetime.utcnow()}
                }
            )
            
            if loot:
                await db.update_one(
                    'pirates',
                    {'user_id': user_id},
                    {'$push': {'inventory.weapons': loot}}
                )
            
            return {
                'type': 'naval_battle',
                'result': 'victory',
                'enemy': enemy['name'],
                'gold_reward': int(gold_reward),
                'xp_reward': xp_reward,
                'loot': loot,
                'rounds': rounds,
                'message': f'⚔️ Defeated {enemy["name"]}! +{int(gold_reward)} gold, +{xp_reward} XP'
            }
        else:
            # Defeat
            gold_lost = random.randint(10, 50)
            
            await db.update_one(
                'pirates',
                {'user_id': user_id},
                {
                    '$inc': {
                        'gold': -gold_lost,
                        'naval_battles_lost': 1
                    },
                    '$set': {'updated_at': datetime.utcnow()}
                }
            )
            
            return {
                'type': 'naval_battle',
                'result': 'defeat',
                'enemy': enemy['name'],
                'gold_lost': gold_lost,
                'rounds': rounds,
                'message': f'💀 Defeated by {enemy["name"]}! Lost {gold_lost} gold.'
            }
    
    @staticmethod
    async def _discover_island(user_id: int) -> dict:
        """Discover a new island"""
        player = await PirateGame.get_player(user_id)
        
        island_names = ['Tortuga', 'Port Royal', 'Nassau', 'Barbados', 'Jamaica', 'Cayman', 'Bermuda']
        island_name = random.choice(island_names)
        
        island = {
            'name': island_name,
            'gold': random.randint(50, 200),
            'defense': random.randint(1, 10),
            'resources': random.randint(10, 50)
        }
        
        # Check if island already exists
        for existing in player['islands']:
            if existing['name'] == island_name:
                return {
                    'type': 'island',
                    'message': f'🏝️ Already discovered {island_name}!'
                }
        
        await db.update_one(
            'pirates',
            {'user_id': user_id},
            {
                '$push': {'islands': island},
                '$inc': {
                    'gold': island['gold'],
                    'xp': random.randint(10, 30)
                },
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
        
        return {
            'type': 'island',
            'name': island_name,
            'gold': island['gold'],
            'message': f'🏝️ Discovered {island_name}! +{island["gold"]} gold!'
        }
    
    @staticmethod
    async def _survive_storm(user_id: int) -> dict:
        """Survive a storm"""
        player = await PirateGame.get_player(user_id)
        
        # Check ship upgrades for survival chance
        survival_chance = 0.5 + player['ship']['upgrades']['hull'] * 0.05
        
        if random.random() < survival_chance:
            # Survived
            damage = random.randint(5, 20)
            await db.update_one(
                'pirates',
                {'user_id': user_id},
                {
                    '$inc': {'gold': -damage},
                    '$set': {'updated_at': datetime.utcnow()}
                }
            )
            return {
                'type': 'storm',
                'result': 'survived',
                'damage': damage,
                'message': f'🌊 Survived the storm! Lost {damage} gold.'
            }
        else:
            # Damaged
            damage = random.randint(20, 50)
            await db.update_one(
                'pirates',
                {'user_id': user_id},
                {
                    '$inc': {'gold': -damage},
                    '$set': {'updated_at': datetime.utcnow()}
                }
            )
            return {
                'type': 'storm',
                'result': 'damaged',
                'damage': damage,
                'message': f'🌊 Storm damaged your ship! Lost {damage} gold.'
            }
    
    @staticmethod
    async def _trade_with_merchant(user_id: int) -> dict:
        """Trade with a merchant"""
        player = await PirateGame.get_player(user_id)
        
        trade_options = [
            {'type': 'buy', 'item': 'Cannons', 'cost': 100, 'benefit': 'attack +5'},
            {'type': 'buy', 'item': 'Supplies', 'cost': 50, 'benefit': 'crew +2'},
            {'type': 'sell', 'item': 'Treasure', 'value': 200}
        ]
        
        trade = random.choice(trade_options)
        
        if trade['type'] == 'buy':
            if player['gold'] >= trade['cost']:
                await db.update_one(
                    'pirates',
                    {'user_id': user_id},
                    {
                        '$inc': {'gold': -trade['cost']},
                        '$set': {'updated_at': datetime.utcnow()}
                    }
                )
                return {
                    'type': 'trade',
                    'result': 'bought',
                    'item': trade['item'],
                    'cost': trade['cost'],
                    'message': f'🛒 Bought {trade["item"]} for {trade["cost"]} gold!'
                }
            else:
                return {
                    'type': 'trade',
                    'result': 'insufficient_funds',
                    'message': '💰 Not enough gold to buy!'
                }
        else:
            # Sell
            if player['treasure'] >= 1:
                await db.update_one(
                    'pirates',
                    {'user_id': user_id},
                    {
                        '$inc': {
                            'gold': trade['value'],
                            'treasure': -1
                        },
                        '$set': {'updated_at': datetime.utcnow()}
                    }
                )
                return {
                    'type': 'trade',
                    'result': 'sold',
                    'item': trade['item'],
                    'value': trade['value'],
                    'message': f'💎 Sold {trade["item"]} for {trade["value"]} gold!'
                }
            else:
                return {
                    'type': 'trade',
                    'result': 'no_treasure',
                    'message': 'No treasure to sell!'
                }
