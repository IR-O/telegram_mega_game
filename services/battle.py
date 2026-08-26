from database.mongodb import db
from datetime import datetime, timedelta
import random
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class BattleService:
    @staticmethod
    async def calculate_battle_outcome(attacker_id: int, defender_id: int) -> Dict[str, Any]:
        """Calculate battle outcome with all factors"""
        # Get player stats
        attacker = await db.find_one('users', {'telegram_id': attacker_id})
        defender = await db.find_one('users', {'telegram_id': defender_id})
        
        if not attacker or not defender:
            return {'error': 'Player not found'}
        
        # Get mafia stats (for combat)
        attacker_mafia = await db.find_one('mafia_players', {'user_id': attacker_id})
        defender_mafia = await db.find_one('mafia_players', {'user_id': defender_id})
        
        if not attacker_mafia or not defender_mafia:
            return {'error': 'Mafia stats not initialized'}
        
        # Calculate attack power
        attacker_attack = attacker_mafia.get('attack', 5) + random.randint(1, 10)
        defender_defense = defender_mafia.get('defense', 5) + random.randint(1, 10)
        
        # Apply weapons and armor bonuses
        weapon_bonus = attacker_mafia.get('weapon_bonus', 0)
        armor_bonus = defender_mafia.get('armor_bonus', 0)
        
        attacker_attack += weapon_bonus
        defender_defense += armor_bonus
        
        # Calculate luck factor
        attacker_luck = random.randint(1, 20)
        defender_luck = random.randint(1, 20)
        
        # Calculate damage
        base_damage = max(1, attacker_attack - defender_defense // 2)
        
        # Critical hit check (10% chance)
        critical = random.random() < 0.1
        if critical:
            base_damage *= 2
        
        # Level advantage
        level_diff = attacker.get('level', 1) - defender.get('level', 1)
        if level_diff > 0:
            base_damage *= (1 + level_diff * 0.1)
        elif level_diff < 0:
            base_damage *= (1 + level_diff * 0.05)
        
        # Determine winner
        attacker_hp = attacker_mafia.get('hp', 100)
        defender_hp = defender_mafia.get('hp', 100)
        
        attacker_damage = base_damage
        defender_damage = max(1, defender_defense // 3 + random.randint(1, 5))
        
        # Simulate battle rounds
        rounds = []
        atk_hp = attacker_hp
        def_hp = defender_hp
        
        while atk_hp > 0 and def_hp > 0:
            # Attacker attacks
            def_hp -= attacker_damage
            rounds.append({
                'round': len(rounds) + 1,
                'attacker_damage': attacker_damage,
                'defender_hp': max(0, def_hp)
            })
            
            if def_hp <= 0:
                break
            
            # Defender attacks
            atk_hp -= defender_damage
            rounds.append({
                'round': len(rounds) + 1,
                'defender_damage': defender_damage,
                'attacker_hp': max(0, atk_hp)
            })
        
        # Determine winner
        if def_hp <= 0:
            winner_id = attacker_id
            loser_id = defender_id
            winner_name = attacker.get('first_name', 'Player')
            loser_name = defender.get('first_name', 'Player')
        else:
            winner_id = defender_id
            loser_id = attacker_id
            winner_name = defender.get('first_name', 'Player')
            loser_name = attacker.get('first_name', 'Player')
        
        # Calculate rewards
        coins_won = random.randint(50, 200) + (attacker.get('level', 1) * 10)
        xp_won = random.randint(20, 50) + (attacker.get('level', 1) * 5)
        respect_won = random.randint(1, 10) + (attacker.get('level', 1) // 2)
        
        # Save battle record
        battle_record = {
            'winner_id': winner_id,
            'loser_id': loser_id,
            'winner_name': winner_name,
            'loser_name': loser_name,
            'coins_won': coins_won,
            'xp_won': xp_won,
            'respect_won': respect_won,
            'rounds': rounds,
            'timestamp': datetime.utcnow(),
            'type': 'pvp'
        }
        await db.insert_one('battles', battle_record)
        
        return {
            'winner': winner_id,
            'loser': loser_id,
            'winner_name': winner_name,
            'loser_name': loser_name,
            'coins_won': coins_won,
            'xp_won': xp_won,
            'respect_won': respect_won,
            'rounds': rounds,
            'critical': critical
        }
    
    @staticmethod
    async def apply_battle_rewards(user_id: int, coins: int, xp: int, respect: int):
        """Apply battle rewards to a player"""
        # Update user stats
        await db.update_one(
            'users',
            {'telegram_id': user_id},
            {
                '$inc': {
                    'coins': coins,
                    'xp': xp,
                    'respect': respect,
                    'total_wins': 1,
                    'games_played': 1
                }
            }
        )
        
        # Check for level up
        user = await db.find_one('users', {'telegram_id': user_id})
        if user:
            xp_needed = user.get('level', 1) * 100
            current_xp = user.get('xp', 0)
            if current_xp >= xp_needed:
                await db.update_one(
                    'users',
                    {'telegram_id': user_id},
                    {
                        '$inc': {'level': 1},
                        '$set': {'xp': current_xp - xp_needed}
                    }
                )
