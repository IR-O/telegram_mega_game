from database.mongodb import db
from datetime import datetime
import random
import logging

logger = logging.getLogger(__name__)

class CityGame:
    @staticmethod
    async def initialize_player(user_id: int) -> dict:
        """Initialize city game player data"""
        city_data = {
            'user_id': user_id,
            'city_name': f"{random.choice(['New', 'Old', 'Great', 'Royal'])} {random.choice(['City', 'Town', 'Village'])}",
            'level': 1,
            'population': 100,
            'happiness': 50,
            'economy': 100,
            'security': 50,
            'income': 10,
            'buildings': {
                'houses': 0,
                'offices': 0,
                'factories': 0,
                'shops': 0,
                'hospitals': 0,
                'police': 0,
                'fire': 0,
                'entertainment': 0
            },
            'xp': 0,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        await db.insert_one('cities', city_data)
        return city_data
    
    @staticmethod
    async def get_player(user_id: int) -> dict:
        """Get city player data"""
        player = await db.find_one('cities', {'user_id': user_id})
        if not player:
            player = await CityGame.initialize_player(user_id)
        return player
    
    @staticmethod
    async def build(user_id: int, building_type: str) -> dict:
        """Build a new building"""
        player = await CityGame.get_player(user_id)
        
        building_costs = {
            'houses': 100,
            'offices': 200,
            'factories': 150,
            'shops': 175,
            'hospitals': 250,
            'police': 200,
            'fire': 180,
            'entertainment': 300
        }
        
        building_benefits = {
            'houses': {'population': 10, 'happiness': 2},
            'offices': {'economy': 15, 'income': 5},
            'factories': {'economy': 20, 'income': 8},
            'shops': {'economy': 10, 'happiness': 3},
            'hospitals': {'happiness': 5, 'security': 2},
            'police': {'security': 10},
            'fire': {'security': 8},
            'entertainment': {'happiness': 10, 'income': 3}
        }
        
        if building_type not in building_costs:
            return {'error': 'Invalid building type!'}
        
        # Check if player has enough resources (simplified)
        # In a real implementation, would check coins from economy
        
        # Build the building
        await db.update_one(
            'cities',
            {'user_id': user_id},
            {
                '$inc': {
                    f'buildings.{building_type}': 1,
                    'population': building_benefits[building_type].get('population', 0),
                    'happiness': building_benefits[building_type].get('happiness', 0),
                    'economy': building_benefits[building_type].get('economy', 0),
                    'income': building_benefits[building_type].get('income', 0),
                    'security': building_benefits[building_type].get('security', 0),
                    'xp': random.randint(5, 15)
                },
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
        
        return {
            'building': building_type,
            'cost': building_costs[building_type],
            'benefits': building_benefits[building_type],
            'message': f'🏗️ Built a {building_type}!'
        }
