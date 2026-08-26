from database.mongodb import db
from datetime import datetime
import random
import logging

logger = logging.getLogger(__name__)

class CardGame:
    @staticmethod
    async def initialize_player(user_id: int) -> dict:
        """Initialize card game player data"""
        card_data = {
            'user_id': user_id,
            'level': 1,
            'xp': 0,
            'rating': 1000,
            'wins': 0,
            'losses': 0,
            'cards': [],
            'deck': [],
            'packs_opened': 0,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        await db.insert_one('cards', card_data)
        return card_data
    
    @staticmethod
    async def get_player(user_id: int) -> dict:
        """Get card game player data"""
        player = await db.find_one('cards', {'user_id': user_id})
        if not player:
            player = await CardGame.initialize_player(user_id)
        return player
    
    @staticmethod
    async def open_pack(user_id: int) -> dict:
        """Open a card pack"""
        player = await CardGame.get_player(user_id)
        
        # Generate cards
        cards_in_pack = []
        rarities = ['Common', 'Common', 'Common', 'Common', 'Rare', 'Rare', 'Epic']
        
        card_types = [
            {'name': 'Warrior', 'attack': 10, 'defense': 5, 'hp': 20},
            {'name': 'Mage', 'attack': 15, 'defense': 3, 'hp': 15},
            {'name': 'Dragon', 'attack': 20, 'defense': 8, 'hp': 30},
            {'name': 'Demon', 'attack': 18, 'defense': 6, 'hp': 25},
            {'name': 'Elf', 'attack': 12, 'defense': 4, 'hp': 18},
            {'name': 'Robot', 'attack': 14, 'defense': 7, 'hp': 22},
            {'name': 'Hero', 'attack': 16, 'defense': 5, 'hp': 24}
        ]
        
        for _ in range(5):
            rarity = random.choice(rarities)
            card_base = random.choice(card_types)
            
            # Apply rarity bonuses
            attack_multiplier = {'Common': 1, 'Rare': 1.2, 'Epic': 1.5, 'Legendary': 2, 'Mythic': 2.5}
            multiplier = attack_multiplier.get(rarity, 1)
            
            card = {
                'id': f"card_{datetime.utcnow().timestamp()}_{random.randint(1000, 9999)}",
                'name': card_base['name'],
                'rarity': rarity,
                'attack': int(card_base['attack'] * multiplier),
                'defense': int(card_base['defense'] * multiplier),
                'hp': int(card_base['hp'] * multiplier),
                'level': 1
            }
            cards_in_pack.append(card)
        
        # Add cards to collection
        await db.update_one(
            'cards',
            {'user_id': user_id},
            {
                '$push': {'cards': {'$each': cards_in_pack}},
                '$inc': {
                    'packs_opened': 1,
                    'xp': random.randint(10, 20)
                },
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
        
        # Find the best card
        best_card = max(cards_in_pack, key=lambda c: c['attack'] + c['defense'])
        
        return {
            'cards': cards_in_pack,
            'best_card': best_card,
            'message': f'📦 Opened pack!\n'
                       f'Got {len(cards_in_pack)} cards\n'
                       f'Best: {best_card["rarity"]} {best_card["name"]}'
        }
