from typing import Any, List

from bson import ObjectId
from pydantic import BaseModel
from werkzeug.security import generate_password_hash, check_password_hash
from models.post import PostResponse, PostBase
from db import db


class UserBase(BaseModel):
    name: str
    password: str
    email: str
    night_mode: bool = False
    post_ids: List[str] = []
    comment_ids: List[str] = []


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    night_mode: bool
    posts: List[PostResponse]


class UserInDB(UserBase):
    password = ""

    def __init__(self, password, **data: Any):
        super().__init__(**data)
        self.password = generate_password_hash(password)

    @classmethod
    async def find_by_email(cls, email):
        user = await db.users.find_one({"email": email})
        if user:
            user["id"] = str(user["_id"])
            user["posts"] = await PostBase.find_by_user_id(user_id=user["id"])
            return UserResponse(**user)
        return None

    @classmethod
    async def find_by_id(cls, _id):
        user = await db.users.find_one({"_id": ObjectId(_id)})
        if user:
            user["id"] = str(user["_id"])
            user["posts"] = await PostBase.find_by_user_id(user_id=user["id"])
            return UserResponse(**user)
        return None

    @classmethod
    async def check_password(cls, email, password):
        user = await db.users.find_one({"email": email})
        if user and check_password_hash(user["password"], password):
            user["id"] = str(user["_id"])
            user["posts"] = await PostBase.find_by_user_id(user_id=user["id"])
            return UserResponse(**user)
        return None

    async def insert(self):
        row = await db.users.insert_one(self.dict())
        if row.acknowledged:
            return row.inserted_id
        return None


class UserUpdates(BaseModel):
    id: str
    name: str
    email: str
    night_mode: bool
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

    async def toggle_night_mode(self, state: bool):
        done = await db.users.update_one({"_id": ObjectId(self.id)}, {"$set": {"night_mode": state}})
        return done.acknowledged

    async def update_user_details(self, updated_details: dict):
        done = await db.users.update_one({"_id": ObjectId(self.id)}, {"$set": updated_details})
        return done.acknowledged

    async def change_password(self, new_password):
        done = await db.users.update_one({"_id": ObjectId(self.id)},
                                         {"$set": {"password": generate_password_hash(new_password)}})
        return done.acknowledged
