import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "appdb")

_client: Optional[AsyncIOMotorClient] = None
db: Optional[AsyncIOMotorDatabase] = None

async def init_db() -> AsyncIOMotorDatabase:
    global _client, db
    if _client is None:
        _client = AsyncIOMotorClient(DATABASE_URL)
        db = _client[DATABASE_NAME]
    return db

async def create_document(collection_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
    database = await init_db()
    now = datetime.utcnow()
    data_with_meta = {**data, "created_at": now, "updated_at": now}
    result = await database[collection_name].insert_one(data_with_meta)
    data_with_meta["_id"] = str(result.inserted_id)
    return data_with_meta

async def get_documents(collection_name: str, filter_dict: Optional[Dict[str, Any]] = None, limit: int = 50) -> List[Dict[str, Any]]:
    database = await init_db()
    cursor = database[collection_name].find(filter_dict or {}).limit(limit)
    docs = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])  # convert ObjectId to string
        docs.append(doc)
    return docs

async def update_document(collection_name: str, filter_dict: Dict[str, Any], update_data: Dict[str, Any]) -> int:
    database = await init_db()
    update_data["updated_at"] = datetime.utcnow()
    result = await database[collection_name].update_many(filter_dict, {"$set": update_data})
    return result.modified_count

async def delete_document(collection_name: str, filter_dict: Dict[str, Any]) -> int:
    database = await init_db()
    result = await database[collection_name].delete_many(filter_dict)
    return result.deleted_count
