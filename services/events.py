from database.mongodb import db
from datetime import datetime, timedelta
import random
import logging

logger = logging.getLogger(__name__)

class EventService:
    EVENT_TYPES = {
        'zombie_outbreak': {
            'name': '🧟 Zombie Outbreak',
            'description': 'Zombies are attacking! Fight them for rewards!',
            'duration': 3600,  # 1 hour
            'rewards': {'coins': 500, 'xp': 200, 'items': ['Medical Kit', 'Ammo']}
        },
        'alien_invasion': {
            'name': '👽 Alien Invasion',
            'description': 'Aliens are invading! Defend the planet!',
            'duration': 7200,  # 2 hours
            'rewards': {'coins': 1000, 'xp': 400, 'items': ['Laser Gun', 'Shield']}
        },
        'pirate_raid': {
            'name': '🏴‍☠️ Pirate Raid',
            'description': 'Pirates are attacking! Defend your treasure!',
            'duration': 3600,
            'rewards': {'coins': 800, 'xp': 300, 'items': ['Treasure Map', 'Cannon']}
        },
        'paranormal_night': {
            'name': '👻 Paranormal Night',
            'description': 'Ghosts are appearing! Investigate the paranormal!',
            'duration': 7200,
            'rewards': {'coins': 600, 'xp': 250, 'items': ['EMF Detector', 'Camera']}
        },
        'dragon_attack': {
            'name': '🐉 Dragon Attack',
            'description': 'A dragon is attacking! Defend your kingdom!',
            'duration': 10800,  # 3 hours
            'rewards': {'coins': 1500, 'xp': 600, 'items': ['Dragon Scale', 'Magic Sword']}
        },
        'mafia_war': {
            'name': '⚔️ Mafia War',
            'description': 'Gang war! Fight for territory and respect!',
            'duration': 14400,  # 4 hours
            'rewards': {'coins': 2000, 'xp': 800, 'items': ['Rare Weapon', 'Armor']}
        }
    }
    
    @staticmethod
    async def check_and_spawn_events():
        """Check and spawn new events"""
        # Check for active events
        active_events = await db.find('global_events', {'active': True})
        
        # End expired events
        now = datetime.utcnow()
        for event in active_events:
            if event.get('end_time', now) <= now:
                await EventService.end_event(event['event_id'])
        
        # Spawn new events (10% chance every check)
        if random.random() < 0.1 and len(active_events) < 2:
            event_type = random.choice(list(EventService.EVENT_TYPES.keys()))
            event_data = EventService.EVENT_TYPES[event_type]
            
            new_event = {
                'event_id': f'event_{datetime.utcnow().timestamp()}',
                'type': event_type,
                'name': event_data['name'],
                'description': event_data['description'],
                'start_time': now,
                'end_time': now + timedelta(seconds=event_data['duration']),
                'active': True,
                'rewards': event_data['rewards'],
                'progress': 0,
                'max_progress': 1000,
                'participants': []
            }
            
            await db.insert_one('global_events', new_event)
            logger.info(f"Global event spawned: {event_data['name']}")
    
    @staticmethod
    async def end_event(event_id: str):
        """End an event and distribute rewards"""
        event = await db.find_one('global_events', {'event_id': event_id})
        if not event:
            return
        
        # Distribute rewards to participants
        participants = event.get('participants', [])
        rewards = event.get('rewards', {})
        
        for participant in participants:
            user_id = participant['user_id']
            participation_level = participant.get('participation', 1)
            
            # Calculate reward based on participation
            coins_reward = rewards.get('coins', 100) * participation_level
            xp_reward = rewards.get('xp', 50) * participation_level
            
            from services.economy import EconomyService
            await EconomyService.add_coins(user_id, coins_reward, f'Event reward: {event["name"]}')
            
            # Add XP
            await db.update_one(
                'users',
                {'telegram_id': user_id},
                {'$inc': {'xp': xp_reward}}
            )
            
            # Check for level up
            user = await db.find_one('users', {'telegram_id': user_id})
            if user and user.get('xp', 0) >= user.get('level', 1) * 100:
                await db.update_one(
                    'users',
                    {'telegram_id': user_id},
                    {
                        '$inc': {'level': 1},
                        '$set': {'xp': user['xp'] - user['level'] * 100}
                    }
                )
        
        # Mark event as inactive
        await db.update_one(
            'global_events',
            {'event_id': event_id},
            {'$set': {'active': False}}
        )
        
        logger.info(f"Event ended: {event['name']}")
