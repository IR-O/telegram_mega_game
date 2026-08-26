from database.mongodb import db
from services.economy import EconomyService
from services.battle import BattleService
from datetime import datetime, timedelta
import random
import logging

logger = logging.getLogger(__name__)

class MafiaGame:
    @staticmethod
    async def initialize_player(user_id: int) -> dict:
        """Initialize mafia player data"""
        mafia_data = {
            'user_id': user_id,
            'level': 1,
            'xp': 0,
            'hp': 100,
            'max_hp': 100,
            'energy': 50,
            'max_energy': 100,
            'attack': 10,
            'defense': 5,
            'luck': 5,
            'cash': 100,
            'bank': 0,
            'respect': 0,
            'wanted_level': 0,
            'gang': None,
            'weapon': None,
            'weapon_bonus': 0,
            'armor': None,
            'armor_bonus': 0,
            'inventory': [],
            'property': None,
            'vehicle': None,
            'mission_cooldown': None,
            'fight_cooldown': None,
            'rob_cooldown': None,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        await db.insert_one('mafia_players', mafia_data)
        return mafia_data
    
    @staticmethod
    async def get_player(user_id: int) -> dict:
        """Get mafia player data"""
        player = await db.find_one('mafia_players', {'user_id': user_id})
        if not player:
            player = await MafiaGame.initialize_player(user_id)
        return player
    
    @staticmethod
    async def fight(attacker_id: int, defender_id: int) -> dict:
        """Handle mafia fight"""
        attacker = await MafiaGame.get_player(attacker_id)
        defender = await MafiaGame.get_player(defender_id)
        
        # Check cooldowns
        if attacker.get('fight_cooldown') and datetime.utcnow() < attacker['fight_cooldown']:
            remaining = (attacker['fight_cooldown'] - datetime.utcnow()).seconds
            return {'error': f'Fight cooldown: {remaining}s remaining'}
        
        # Calculate battle
        result = await BattleService.calculate_battle_outcome(attacker_id, defender_id)
        
        if 'error' in result:
            return result
        
        # Update player stats
        winner_id = result['winner']
        loser_id = result['loser']
        
        # Update HP
        if winner_id == attacker_id:
            # Attacker won
            await db.update_one(
                'mafia_players',
                {'user_id': attacker_id},
                {
                    '$inc': {
                        'xp': result['xp_won'],
                        'cash': result['coins_won'],
                        'respect': result['respect_won']
                    },
                    '$set': {
                        'fight_cooldown': datetime.utcnow() + timedelta(minutes=1),
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            await db.update_one(
                'mafia_players',
                {'user_id': defender_id},
                {
                    '$inc': {
                        'hp': -random.randint(10, 30)
                    },
                    '$set': {
                        'updated_at': datetime.utcnow()
                    }
                }
            )
        else:
            # Defender won
            await db.update_one(
                'mafia_players',
                {'user_id': defender_id},
                {
                    '$inc': {
                        'xp': result['xp_won'],
                        'cash': result['coins_won'],
                        'respect': result['respect_won']
                    },
                    '$set': {
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            await db.update_one(
                'mafia_players',
                {'user_id': attacker_id},
                {
                    '$inc': {
                        'hp': -random.randint(10, 30)
                    },
                    '$set': {
                        'fight_cooldown': datetime.utcnow() + timedelta(minutes=1),
                        'updated_at': datetime.utcnow()
                    }
                }
            )
        
        return result
    
    @staticmethod
    async def rob(robber_id: int, target_id: int) -> dict:
        """Handle robbery attempt"""
        robber = await MafiaGame.get_player(robber_id)
        target = await MafiaGame.get_player(target_id)
        
        # Check cooldowns
        if robber.get('rob_cooldown') and datetime.utcnow() < robber['rob_cooldown']:
            remaining = (robber['rob_cooldown'] - datetime.utcnow()).seconds
            return {'error': f'Rob cooldown: {remaining}s remaining'}
        
        # Calculate robbery outcome
        luck = robber.get('luck', 5)
        level = robber.get('level', 1)
        weapon_bonus = robber.get('weapon_bonus', 0)
        target_security = target.get('defense', 5)
        
        # Random factors
        random_factor = random.randint(1, 20)
        success_chance = min(90, 30 + (luck * 2) + (level * 1) + (weapon_bonus * 0.5) - (target_security * 1.5))
        
        # Determine outcome
        roll = random.randint(1, 100)
        
        if roll < success_chance:
            # Success!
            amount = random.randint(10, 50) * max(1, level)
            actual_amount = min(amount, target.get('cash', 0))
            
            if actual_amount > 0:
                await db.update_one(
                    'mafia_players',
                    {'user_id': robber_id},
                    {
                        '$inc': {'cash': actual_amount},
                        '$set': {
                            'rob_cooldown': datetime.utcnow() + timedelta(minutes=5),
                            'updated_at': datetime.utcnow()
                        }
                    }
                )
                
                await db.update_one(
                    'mafia_players',
                    {'user_id': target_id},
                    {
                        '$inc': {'cash': -actual_amount},
                        '$set': {'updated_at': datetime.utcnow()}
                    }
                )
                
                return {
                    'result': 'success',
                    'amount': actual_amount,
                    'message': f'🎉 Success! Stole {actual_amount} coins!'
                }
            else:
                return {
                    'result': 'empty',
                    'message': '😅 Target has no cash to steal!'
                }
        elif roll < success_chance + 10:
            # Partial success
            amount = random.randint(1, 20) * max(1, level // 2)
            actual_amount = min(amount, target.get('cash', 0))
            
            if actual_amount > 0:
                await db.update_one(
                    'mafia_players',
                    {'user_id': robber_id},
                    {
                        '$inc': {'cash': actual_amount},
                        '$set': {
                            'rob_cooldown': datetime.utcnow() + timedelta(minutes=5),
                            'updated_at': datetime.utcnow()
                        }
                    }
                )
                
                await db.update_one(
                    'mafia_players',
                    {'user_id': target_id},
                    {
                        '$inc': {'cash': -actual_amount},
                        '$set': {'updated_at': datetime.utcnow()}
                    }
                )
                
                return {
                    'result': 'partial',
                    'amount': actual_amount,
                    'message': f'⚠️ Partial success! Stole {actual_amount} coins.'
                }
            else:
                return {
                    'result': 'empty',
                    'message': '😅 Target has no cash to steal!'
                }
        else:
            # Failed - caught
            penalty = random.randint(10, 50) * max(1, level // 2)
            
            await db.update_one(
                'mafia_players',
                {'user_id': robber_id},
                {
                    '$inc': {
                        'cash': -penalty,
                        'wanted_level': 1
                    },
                    '$set': {
                        'rob_cooldown': datetime.utcnow() + timedelta(minutes=10),
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            return {
                'result': 'caught',
                'amount': penalty,
                'message': f'🚨 Caught! Lost {penalty} coins. Wanted level increased!'
            }
    
    @staticmethod
    async def work(user_id: int) -> dict:
        """Handle mafia work"""
        player = await MafiaGame.get_player(user_id)
        
        # Check energy
        if player.get('energy', 0) < 10:
            return {'error': 'Not enough energy! Need 10 energy to work.'}
        
        jobs = [
            {'name': 'Street Racer', 'min': 50, 'max': 150, 'energy': 10},
            {'name': 'Hacker', 'min': 100, 'max': 300, 'energy': 15},
            {'name': 'Driver', 'min': 80, 'max': 200, 'energy': 12},
            {'name': 'Dealer', 'min': 150, 'max': 400, 'energy': 20},
            {'name': 'Bodyguard', 'min': 120, 'max': 250, 'energy': 15},
            {'name': 'Mercenary', 'min': 200, 'max': 500, 'energy': 25},
            {'name': 'Businessman', 'min': 300, 'max': 800, 'energy': 30}
        ]
        
        job = random.choice(jobs)
        earned = random.randint(job['min'], job['max'])
        
        # Apply level bonus
        level_bonus = player.get('level', 1) * 5
        earned += level_bonus
        
        # Update player
        await db.update_one(
            'mafia_players',
            {'user_id': user_id},
            {
                '$inc': {
                    'cash': earned,
                    'xp': random.randint(10, 30),
                    'energy': -job['energy']
                },
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
        
        return {
            'job': job['name'],
            'earned': earned,
            'energy_used': job['energy'],
            'xp_gained': random.randint(10, 30)
        }
