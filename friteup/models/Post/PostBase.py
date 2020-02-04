from bson import ObjectId
from pydantic import BaseModel
from typing import List, Any
import pymongo

import utils.model_utils.user as UserUtils
from models.comment import CommentBase, CommentResponse
from models.User.UserResponse import UserResponse
from models.Post.PostResponse import PostResponse
from models.Post.PostResponseWithUser import PostResponseWithUser
from db.mongodb import get_database


class PostBase(BaseModel):
    text: str
    title: str
    created_at: float
    published: bool
    user_id: str
    up_vote: List[str] = []
    down_vote: List[str] = []
    comment_ids: List[str] = []

    def add_new_comment(self, comment_id):
        self.comment_ids.insert(comment_id)

    @classmethod
    async def search_posts(cls, keyword):
        db = await get_database()
        resp = []
        posts = await db.posts.find(
            {
                "$text": {
                    "$search": keyword
                }
            }).to_list(None)
        for post in posts:
            post["id"] = str(post["_id"])
            post["user"] = await UserUtils.find_user_by_id(
                post["user_id"],
                False,
                False
            )
            post["comments"] = await CommentBase.find_by_post_id(post["id"])
            resp.append(PostResponseWithUser(**post))
        return resp

    async def add_comment(self, comment_id: str, user_id: str):
        db = await get_database()
        self.comment_ids.append(comment_id)
        done = await db.users.update_one({"_id": ObjectId(user_id)},
                                         {"$set": {
                                             "comment_ids": self.comment_ids
                                         }})
        return done

    async def insert(self):
        db = await get_database()
        row = await db.posts.insert_one(self.dict())
        if row.acknowledged:
            await db.posts.create_index([
                ("text", pymongo.TEXT),
                ("title", pymongo.TEXT)
            ])
            return row.inserted_id
        return None
