import os
from typing import Any, Dict, List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "appdb")

_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None

async def connect_db() -> AsyncIOMotorDatabase:
    global _client, _db
    if _db is None:
        _client = AsyncIOMotorClient(DATABASE_URL)
        _db = _client[DATABASE_NAME]
    return _db

# Exported alias per platform guidance
async def get_db() -> AsyncIOMotorDatabase:
    return await connect_db()

# Convenience used in instructions
async def create_document(collection_name: str, data: Dict[str, Any]) -> str:
    db = await get_db()
    now = datetime.utcnow().isoformat()
    payload = {**data, "created_at": now, "updated_at": now}
    result = await db[collection_name].insert_one(payload)
    return str(result.inserted_id)

async def get_documents(collection_name: str, filter_dict: Optional[Dict[str, Any]] = None, limit: int = 0) -> List[Dict[str, Any]]:
    db = await get_db()
    cursor = db[collection_name].find(filter_dict or {})
    if limit and limit > 0:
        cursor = cursor.limit(limit)
    docs = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])  # stringify ObjectId
        docs.append(doc)
    return docs

async def get_one(collection_name: str, filter_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    db = await get_db()
    doc = await db[collection_name].find_one(filter_dict)
    if doc:
        doc["_id"] = str(doc["_id"])  # stringify ObjectId
    return doc
