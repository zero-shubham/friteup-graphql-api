from pydantic import BaseModel
from db.mongodb import get_database


class TokenBase(BaseModel):
    user_id: str
    token: str

    @classmethod
    async def find_by_user_id(cls, _id):
        db = await get_database()
        token = await db.tokens.find_one({"_id": _id})
        if token:
            return token
        return None

    async def insert(self):
        db = await get_database()
        if db.tokens.find_one({"_id": self.user_id}):
            row = await db.tokens.update_one({"_id": self.user_id}, {"$set": {"token": self.token}}, upsert=True)
            return row.upserted_id
        else:
            row = await db.tokens.insert_one({"_id": self.user_id, "token": self.token})
            if row.acknowledged:
                return row.inserted_id
        return None

    @classmethod
    async def delete(cls, user_id):
        db = await get_database()
        deleted_token = await db.tokens.delete_one({"_id": user_id})
        if deleted_token.acknowledged:
            return True
        return None
