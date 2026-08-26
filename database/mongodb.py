from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from typing import Optional, Dict, Any, List
from config import Config
import logging

logger = logging.getLogger(__name__)

class MongoDB:
    _instance: Optional['MongoDB'] = None
    _client: Optional[AsyncIOMotorClient] = None
    _db: Optional[Any] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def connect(self):
        if self._client is None:
            try:
                self._client = AsyncIOMotorClient(Config.MONGO_DB_URI)
                self._db = self._client[Config.DATABASE_NAME]
                await self._client.admin.command('ping')
                logger.info("Connected to MongoDB successfully")
                await self._create_indexes()
            except Exception as e:
                logger.error(f"Failed to connect to MongoDB: {e}")
                raise
    
    async def _create_indexes(self):
        """Create necessary indexes"""
        try:
            # Users collection
            await self._db.users.create_index('telegram_id', unique=True)
            await self._db.users.create_index('username')
            await self._db.users.create_index('level')
            await self._db.users.create_index('last_active')
            
            # Economy collection
            await self._db.economy.create_index('user_id', unique=True)
            
            # Transactions
            await self._db.transactions.create_index('user_id')
            await self._db.transactions.create_index('timestamp')
            await self._db.transactions.create_index('type')
            
            # Battles
            await self._db.battles.create_index('winner_id')
            await self._db.battles.create_index('loser_id')
            await self._db.battles.create_index('timestamp')
            
            # Gangs
            await self._db.gangs.create_index('gang_id', unique=True)
            await self._db.gangs.create_index('level')
            await self._db.gangs.create_index('power')
            
            # Gang members
            await self._db.gang_members.create_index('user_id', unique=True)
            await self._db.gang_members.create_index('gang_id')
            
            # Group worlds
            await self._db.group_worlds.create_index('group_id', unique=True)
            
            # Global events
            await self._db.global_events.create_index('active')
            await self._db.global_events.create_index('end_time')
            
            # Cooldowns
            await self._db.cooldowns.create_index('user_id')
            await self._db.cooldowns.create_index('expires_at')
            
            logger.info("MongoDB indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
    
    @property
    def db(self):
        if self._db is None:
            raise Exception("Database not connected. Call connect() first.")
        return self._db
    
    async def close(self):
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            logger.info("MongoDB connection closed")
    
    # Helper methods
    async def find_one(self, collection: str, filter: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self.db[collection].find_one(filter)
    
    async def find(self, collection: str, filter: Dict[str, Any], **kwargs) -> List[Dict[str, Any]]:
        cursor = self.db[collection].find(filter, **kwargs)
        return await cursor.to_list(length=kwargs.get('limit', 100))
    
    async def insert_one(self, collection: str, document: Dict[str, Any]) -> str:
        result = await self.db[collection].insert_one(document)
        return str(result.inserted_id)
    
    async def update_one(self, collection: str, filter: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        result = await self.db[collection].update_one(filter, update)
        return {
            'matched_count': result.matched_count,
            'modified_count': result.modified_count
        }
    
    async def update_many(self, collection: str, filter: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        result = await self.db[collection].update_many(filter, update)
        return {
            'matched_count': result.matched_count,
            'modified_count': result.modified_count
        }
    
    async def delete_one(self, collection: str, filter: Dict[str, Any]) -> int:
        result = await self.db[collection].delete_one(filter)
        return result.deleted_count
    
    async def delete_many(self, collection: str, filter: Dict[str, Any]) -> int:
        result = await self.db[collection].delete_many(filter)
        return result.deleted_count
    
    async def aggregate(self, collection: str, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        cursor = self.db[collection].aggregate(pipeline)
        return await cursor.to_list(length=None)

# Global database instance
db = MongoDB()
