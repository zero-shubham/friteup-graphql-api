from typing import Any, List
import pymongo
from bson import ObjectId
from pydantic import BaseModel
from werkzeug.security import generate_password_hash, check_password_hash

import utils.model_utils.post as PostUtils
from models.Post.PostBase import PostBase
from models.Post.PostResponse import PostResponse
from models.User.UserBase import UserBase
from models.User.UserResponse import UserResponse
from db import db


class UserInDB(UserBase):
    password = ""

    def __init__(self, password, **data: Any):
        super().__init__(**data)
        self.password = generate_password_hash(password)

    @classmethod
    async def check_password(cls, email, password, is_authenticated):
        user = await db.users.find_one({"email": email})
        if user and check_password_hash(user["password"], password):
            user["id"] = str(user["_id"])
            user["posts"] = await PostUtils.find_posts_by_user_id(
                user_id=user["id"],
                is_authenticated=is_authenticated
            )
            return UserResponse(**user)
        return None

    @classmethod
    async def search_users(cls, keyword, current_user_id):
        resp = []
        users = await db.users.find(
            {
                "$text": {
                    "$search": keyword
                }
            }).to_list(None)

        for user in users:
            if str(user["_id"]) != current_user_id:
                user["id"] = str(user["_id"])
                user["posts"] = await PostUtils.find_posts_by_user_id(
                    user_id=user["id"],
                    is_authenticated=False
                )
                resp.append(UserResponse(**user))
        return resp

    async def insert(self):
        row = await db.users.insert_one(self.dict())
        if row.acknowledged:
            await db.users.create_index([("name", pymongo.TEXT)])
            return row.inserted_id
        return None
