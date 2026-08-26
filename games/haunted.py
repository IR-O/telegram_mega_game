from database.mongodb import db
from datetime import datetime
import random
import logging

logger = logging.getLogger(__name__)

class HauntedGame:
    @staticmethod
    async def initialize_player(user_id: int) -> dict:
        """Initialize haunted game player data"""
        haunted_data = {
            'user_id': user_id,
            'level': 1,
            'xp': 0,
            'location': 'abandoned_house',
            'ghosts_found': 0,
            'evidence_collected': 0,
            'equipment': ['flashlight'],
            'investigations': 0,
            'ghosts': [],
            'evidence': [],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        await db.insert_one('haunted_worlds', haunted_data)
        return haunted_data
    
    @staticmethod
    async def get_player(user_id: int) -> dict:
        """Get haunted player data"""
        player = await db.find_one('haunted_worlds', {'user_id': user_id})
        if not player:
            player = await HauntedGame.initialize_player(user_id)
        return player
    
    @staticmethod
    async def investigate(user_id: int) -> dict:
        """Investigate a location"""
        player = await HauntedGame.get_player(user_id)
        
        locations = [
            {'name': 'Abandoned House', 'ghost_chance': 0.3, 'evidence_chance': 0.4},
            {'name': 'Haunted Hospital', 'ghost_chance': 0.4, 'evidence_chance': 0.3},
            {'name': 'Dark Forest', 'ghost_chance': 0.25, 'evidence_chance': 0.35},
            {'name': 'Cemetery', 'ghost_chance': 0.35, 'evidence_chance': 0.25},
            {'name': 'Underground Tunnels', 'ghost_chance': 0.45, 'evidence_chance': 0.2}
        ]
        
        location = random.choice(locations)
        
        # Investigation results
        results = []
        
        # Check for ghost encounter
        if random.random() < location['ghost_chance']:
            ghost = await HauntedGame._encounter_ghost(user_id)
            results.append(ghost)
        
        # Check for evidence
        if random.random() < location['evidence_chance']:
            evidence = await HauntedGame._collect_evidence(user_id)
            results.append(evidence)
        
        # Update investigation count
        await db.update_one(
            'haunted_worlds',
            {'user_id': user_id},
            {
                '$inc': {'investigations': 1},
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
        
        if not results:
            return {
                'type': 'investigation',
                'result': 'nothing',
                'location': location['name'],
                'message': f'🔍 Investigated {location["name"]} but found nothing.'
            }
        
        return {
            'type': 'investigation',
            'location': location['name'],
            'results': results,
            'message': f'🔍 Investigated {location["name"]}:\n' + '\n'.join([r['message'] for r in results])
        }
    
    @staticmethod
    async def _encounter_ghost(user_id: int) -> dict:
        """Encounter a ghost"""
        player = await HauntedGame.get_player(user_id)
        
        ghost_types = [
            {'name': 'Poltergeist', 'strength': 5, 'reward': 20},
            {'name': 'Shadow Ghost', 'strength': 10, 'reward': 40},
            {'name': 'Banshee', 'strength': 15, 'reward': 60},
            {'name': 'Demon', 'strength': 20, 'reward': 80},
            {'name': 'Boss Ghost', 'strength': 30, 'reward': 150}
        ]
        
        ghost = random.choice(ghost_types)
        
        # Check equipment for bonus
        equipment_bonus = 0
        if 'emf_detector' in player['equipment']:
            equipment_bonus += 5
        if 'spirit_detector' in player['equipment']:
            equipment_bonus += 10
        if 'camera' in player['equipment']:
            equipment_bonus += 3
        
        # Fight or flee
        if random.random() < 0.6 + (player['level'] * 0.01):
            # Victory
            reward = ghost['reward'] * (1 + player['level'] * 0.1)
            xp_reward = random.randint(10, 30) * (1 + player['level'] * 0.05)
            
            # Add ghost to collection
            new_ghost = {
                'name': ghost['name'],
                'strength': ghost['strength'],
                'collected_at': datetime.utcnow()
            }
            
            await db.update_one(
                'haunted_worlds',
                {'user_id': user_id},
                {
                    '$push': {'ghosts': new_ghost},
                    '$inc': {
                        'ghosts_found': 1,
                        'xp': int(xp_reward)
                    },
                    '$set': {'updated_at': datetime.utcnow()}
                }
            )
            
            return {
                'type': 'ghost_encounter',
                'result': 'victory',
                'ghost': ghost['name'],
                'reward': int(reward),
                'xp_reward': int(xp_reward),
                'message': f'👻 Defeated {ghost["name"]}! +{int(reward)} xp'
            }
        else:
            # Defeat
            await db.update_one(
                'haunted_worlds',
                {'user_id': user_id},
                {'$set': {'updated_at': datetime.utcnow()}}
            )
            
            return {
                'type': 'ghost_encounter',
                'result': 'defeat',
                'ghost': ghost['name'],
                'message': f'💀 Overwhelmed by {ghost["name"]}!'
            }
    
    @staticmethod
    async def _collect_evidence(user_id: int) -> dict:
        """Collect evidence"""
        player = await HauntedGame.get_player(user_id)
        
        evidence_types = [
            'EMF Reading', 'Ghost Photo', 'Recording', 'Temperature Drop',
            'Mysterious Writing', 'Footprints', 'Unusual Smell'
        ]
        
        evidence = random.choice(evidence_types)
        
        # Check if evidence already collected
        if evidence in player['evidence']:
            return {
                'type': 'evidence',
                'result': 'duplicate',
                'evidence': evidence,
                'message': f'📊 Already collected {evidence} evidence.'
            }
        
        await db.update_one(
            'haunted_worlds',
            {'user_id': user_id},
            {
                '$push': {'evidence': evidence},
                '$inc': {
                    'evidence_collected': 1,
                    'xp': random.randint(5, 15)
                },
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
        
        return {
            'type': 'evidence',
            'result': 'new',
            'evidence': evidence,
            'message': f'📊 Collected {evidence} evidence!'
        }
