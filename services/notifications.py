from database.mongodb import db
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    async def process_notifications():
        """Process pending notifications"""
        try:
            # Get pending notifications
            notifications = await db.find('notifications', {
                'processed': False,
                'send_at': {'$lte': datetime.utcnow()}
            })
            
            for notification in notifications:
                # Send notification to user
                # This would integrate with Telegram API
                # For now, we'll mark as processed
                await db.update_one(
                    'notifications',
                    {'_id': notification['_id']},
                    {'$set': {'processed': True}}
                )
                
        except Exception as e:
            logger.error(f"Error processing notifications: {e}")
    
    @staticmethod
    async def add_notification(user_id: int, message: str, delay_seconds: int = 0):
        """Add a notification for a user"""
        notification = {
            'user_id': user_id,
            'message': message,
            'send_at': datetime.utcnow() + timedelta(seconds=delay_seconds),
            'processed': False,
            'created_at': datetime.utcnow()
        }
        
        await db.insert_one('notifications', notification)
        
        # Check if user has notifications enabled
        user = await db.find_one('users', {'telegram_id': user_id})
        if user and user.get('settings', {}).get('notifications', True):
            return True
        return False
