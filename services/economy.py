from database.mongodb import db
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import random
import logging

logger = logging.getLogger(__name__)

class EconomyService:
    @staticmethod
    async def initialize_user(user_id: int):
        """Initialize economy for a new user"""
        economy_data = {
            'user_id': user_id,
            'coins': 1000,
            'gems': 10,
            'bank': 0,
            'total_earned': 0,
            'total_spent': 0,
            'total_gems_earned': 0,
            'last_daily': None,
            'daily_streak': 0,
            'properties': [],
            'businesses': [],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        await db.insert_one('economy', economy_data)
        
        # Create initial transaction
        await EconomyService.log_transaction(
            user_id,
            'initial_bonus',
            1000,
            'Initial bonus'
        )
    
    @staticmethod
    async def get_balance(user_id: int) -> Dict[str, Any]:
        """Get user's balance"""
        economy = await db.find_one('economy', {'user_id': user_id})
        if not economy:
            await EconomyService.initialize_user(user_id)
            economy = await db.find_one('economy', {'user_id': user_id})
        
        return {
            'coins': economy.get('coins', 0),
            'gems': economy.get('gems', 0),
            'bank': economy.get('bank', 0)
        }
    
    @staticmethod
    async def add_coins(user_id: int, amount: int, reason: str) -> bool:
        """Add coins to user's account with validation"""
        if amount <= 0:
            return False
        
        # Get user's current balance
        economy = await db.find_one('economy', {'user_id': user_id})
        if not economy:
            await EconomyService.initialize_user(user_id)
            economy = await db.find_one('economy', {'user_id': user_id})
        
        # Check maximum limit
        new_balance = economy.get('coins', 0) + amount
        if new_balance > 10**9:  # Max 1 billion
            return False
        
        # Update with atomic operation
        result = await db.update_one(
            'economy',
            {'user_id': user_id},
            {
                '$inc': {
                    'coins': amount,
                    'total_earned': amount
                },
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
        
        if result['modified_count'] > 0:
            await EconomyService.log_transaction(
                user_id,
                'add_coins',
                amount,
                reason
            )
            return True
        return False
    
    @staticmethod
    async def remove_coins(user_id: int, amount: int, reason: str) -> bool:
        """Remove coins from user's account with validation"""
        if amount <= 0:
            return False
        
        # Get user's current balance
        economy = await db.find_one('economy', {'user_id': user_id})
        if not economy:
            await EconomyService.initialize_user(user_id)
            economy = await db.find_one('economy', {'user_id': user_id})
        
        current_balance = economy.get('coins', 0)
        if current_balance < amount:
            return False  # Insufficient funds
        
        # Update with atomic operation
        result = await db.update_one(
            'economy',
            {'user_id': user_id, 'coins': {'$gte': amount}},
            {
                '$inc': {'coins': -amount},
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
        
        if result['modified_count'] > 0:
            await EconomyService.log_transaction(
                user_id,
                'remove_coins',
                -amount,
                reason
            )
            return True
        return False
    
    @staticmethod
    async def add_gems(user_id: int, amount: int, reason: str) -> bool:
        """Add gems to user's account"""
        if amount <= 0:
            return False
        
        result = await db.update_one(
            'economy',
            {'user_id': user_id},
            {
                '$inc': {
                    'gems': amount,
                    'total_gems_earned': amount
                },
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
        
        if result['modified_count'] > 0:
            await EconomyService.log_transaction(
                user_id,
                'add_gems',
                amount,
                reason
            )
            return True
        return False
    
    @staticmethod
    async def log_transaction(user_id: int, transaction_type: str, amount: int, description: str):
        """Log a transaction"""
        transaction = {
            'user_id': user_id,
            'type': transaction_type,
            'amount': amount,
            'description': description,
            'timestamp': datetime.utcnow()
        }
        await db.insert_one('transactions', transaction)
    
    @staticmethod
    async def claim_daily(user_id: int) -> Dict[str, Any]:
        """Claim daily reward with streak tracking"""
        economy = await db.find_one('economy', {'user_id': user_id})
        if not economy:
            await EconomyService.initialize_user(user_id)
            economy = await db.find_one('economy', {'user_id': user_id})
        
        last_daily = economy.get('last_daily')
        today = datetime.utcnow().date()
        
        # Check if already claimed today
        if last_daily and last_daily.date() == today:
            return {'claimed': False, 'message': 'Already claimed today!'}
        
        # Calculate streak
        streak = economy.get('daily_streak', 0)
        if last_daily and last_daily.date() == today - timedelta(days=1):
            streak += 1
        else:
            streak = 1
        
        # Calculate rewards with streak bonus
        base_coins = 1000
        base_gems = 5
        bonus_coins = streak * 100
        bonus_gems = streak
        
        # Apply streak bonuses at milestones
        if streak >= 7:
            bonus_coins += 500
        if streak >= 30:
            bonus_coins += 2000
        
        total_coins = base_coins + bonus_coins
        total_gems = base_gems + bonus_gems
        
        # Update economy
        await db.update_one(
            'economy',
            {'user_id': user_id},
            {
                '$inc': {
                    'coins': total_coins,
                    'gems': total_gems,
                    'total_earned': total_coins
                },
                '$set': {
                    'last_daily': datetime.utcnow(),
                    'daily_streak': streak,
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        await EconomyService.log_transaction(
            user_id,
            'daily_reward',
            total_coins,
            f'Daily reward - Streak: {streak} days'
        )
        
        return {
            'claimed': True,
            'coins': total_coins,
            'gems': total_gems,
            'streak': streak,
            'message': f'Daily reward claimed! +{total_coins} coins, +{total_gems} gems (Streak: {streak} days)'
        }
    
    @staticmethod
    async def bank_deposit(user_id: int, amount: int) -> bool:
        """Deposit coins into bank"""
        if amount <= 0:
            return False
        
        economy = await db.find_one('economy', {'user_id': user_id})
        if not economy:
            return False
        
        if economy.get('coins', 0) < amount:
            return False
        
        # Atomic operation
        result = await db.update_one(
            'economy',
            {'user_id': user_id, 'coins': {'$gte': amount}},
            {
                '$inc': {
                    'coins': -amount,
                    'bank': amount
                },
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
        
        if result['modified_count'] > 0:
            await EconomyService.log_transaction(
                user_id,
                'bank_deposit',
                amount,
                'Bank deposit'
            )
            return True
        return False
    
    @staticmethod
    async def bank_withdraw(user_id: int, amount: int) -> bool:
        """Withdraw coins from bank"""
        if amount <= 0:
            return False
        
        economy = await db.find_one('economy', {'user_id': user_id})
        if not economy:
            return False
        
        if economy.get('bank', 0) < amount:
            return False
        
        result = await db.update_one(
            'economy',
            {'user_id': user_id, 'bank': {'$gte': amount}},
            {
                '$inc': {
                    'coins': amount,
                    'bank': -amount
                },
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
        
        if result['modified_count'] > 0:
            await EconomyService.log_transaction(
                user_id,
                'bank_withdraw',
                -amount,
                'Bank withdrawal'
            )
            return True
        return False
