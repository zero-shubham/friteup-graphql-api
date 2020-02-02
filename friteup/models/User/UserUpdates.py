from pydantic import BaseModel
from bson import ObjectId
from werkzeug.security import generate_password_hash
from typing import List, Any
from db import db


class UserUpdates(BaseModel):
    id: str
    name: str
    email: str
    night_mode: bool
    bio: str = ""
    subscribers: List[str] = []
    subscribed: List[str] = []
    post_ids: List[str] = []
    comment_ids: List[str] = []

    @classmethod
    async def find_by_id(cls, _id):
        user = await db.users.find_one({"_id": ObjectId(_id)})
        if user:
            user["id"] = str(user["_id"])
            return UserUpdates(**user)
        return None

    async def add_comment(self, comment_id: str):
        self.comment_ids.append(comment_id)
        done = await db.users.update_one({"_id": ObjectId(self.id)},
                                         {"$set": {"comment_ids": self.comment_ids}})
        return done

    async def add_post(self, post_id: str):
        self.post_ids.append(str(post_id))
        done = await db.users.update_one({"_id": ObjectId(self.id)}, {"$set": {"post_ids": self.post_ids}})
        return done

    async def delete(self):
        done = await db.users.delete_one({"_id": ObjectId(self.id)})
        return done.acknowledged

    async def update_user_details(self, updated_details: dict):
        done = await db.users.update_one(
            {"_id": ObjectId(self.id)},
            {"$set": updated_details}
        )
        return done.acknowledged

    async def change_password(self, new_password):
        done = await db.users.update_one(
            {
                "_id": ObjectId(self.id)
            },
            {
                "$set": {
                    "password": generate_password_hash(new_password)
                }
            }
        )
        return done.acknowledged

    async def add_subscriber(self, user_id):
        self.subscribers.append(user_id)
        done = await db.users.update_one(
            {"_id": ObjectId(self.id)},
            {
                "$set": {
                    "subscribers": self.subscribers
                }
            }
        )
        return done.acknowledged

    async def add_subscribed(self, user_id):
        self.subscribed.append(user_id)
        done = await db.users.update_one(
            {"_id": ObjectId(self.id)},
            {
                "$set": {
                    "subscribed": self.subscribed
                }
            }
        )
        return done.acknowledged
    
    async def remove_subscriber(self, user_id):
        self.subscribers.remove(user_id)
        done = await db.users.update_one(
            {"_id": ObjectId(self.id)},
            {
                "$set": {
                    "subscribers": self.subscribers
                }
            }
        )
        return done.acknowledged

    async def remove_subscribed(self, user_id):
        self.subscribed.remove(user_id)
        done = await db.users.update_one(
            {"_id": ObjectId(self.id)},
            {
                "$set": {
                    "subscribed": self.subscribed
                }
            }
        )
        return done.acknowledged
    
