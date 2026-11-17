from datetime import UTC, datetime

from bson import ObjectId


def public_user(user: dict) -> dict:
    """Convert a MongoDB user document to a safe API response."""
    user["_id"] = str(user["_id"])
    user.pop("hash_pass", None)
    return user


async def create_user(db, user_data: dict) -> dict:
    now = datetime.now(UTC)
    user_data.update(created_at=now, updated_at=None)
    result = await db["users"].insert_one(user_data)
    return public_user(await db["users"].find_one({"_id": result.inserted_id}))


async def list_users(db) -> list[dict]:
    users = await db["users"].find({}, {"hash_pass": 0}).to_list(length=100)
    return [public_user(user) for user in users]


async def get_user(db, user_id: ObjectId) -> dict | None:
    user = await db["users"].find_one({"_id": user_id}, {"hash_pass": 0})
    return public_user(user) if user else None


async def update_user(db, user_id: ObjectId, changes: dict) -> dict | None:
    if not changes:
        return await get_user(db, user_id)

    changes["updated_at"] = datetime.now(UTC)
    await db["users"].update_one({"_id": user_id}, {"$set": changes})
    return await get_user(db, user_id)

async def delete_user(db, user_id: ObjectId) -> bool:
    result = await db["users"].delete_one({"_id": user_id})
    return result.deleted_count == 1
