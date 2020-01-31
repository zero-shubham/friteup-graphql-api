from bson import ObjectId
from pydantic import BaseModel
from typing import List, Any
import pymongo
from models.comment import CommentBase, CommentResponse
from models.User.UserResponse import UserResponse
from db import db
from models.Post.PostResponse import PostResponse
from models.Post.PostResponseWithUser import PostResponseWithUser


async def find_user_by_id(_id):
    user = await db.users.find_one({"_id": ObjectId(_id)})
    if user:
        user["id"] = str(user["_id"])
        user["posts"] = []
        return UserResponse(**user)
    return None


class PostBase(BaseModel):
    text: str
    title: str
    createdAt: float
    published: bool
    user_id: str
    up_vote: int = 0
    down_vote: int = 0
    comment_ids: List[str] = []

    def add_new_comment(self, comment_id):
        self.comment_ids.insert(comment_id)

    @classmethod
    async def find_by_id(cls, _id, is_authenticated):
        post = None
        if is_authenticated:
            post = await db.posts.find_one({"_id": ObjectId(_id)})
        else:
            post = await db.posts.find_one({
                "_id": ObjectId(_id),
                "published": True
            })
            
        if post:
            post["id"] = str(post["_id"])
            post["user"] = await find_user_by_id(_id=post["user_id"])
            post["comments"] = await CommentBase.find_by_post_id(post["id"])
            return PostResponse(**post)
        return None

    @classmethod
    async def find_by_user_id(
        cls,
        user_id,
        is_authenticated,
        withActualUser=False
    ):
        # if the req is authenticated then send back all the posts else send
        # only published posts
        posts = None
        if is_authenticated:
            posts_count = await db.posts.count_documents({"user_id": user_id})
            posts = db.posts.find({"user_id": user_id})
        else:
            posts_count = await db.posts.count_documents({
                "user_id": user_id,
                "published": True
            })
            posts = db.posts.find({
                "user_id": user_id,
                "published": True
            })
        if posts:
            posts = await posts.to_list(posts_count)
            all_posts = []
            for post in posts:
                post["id"] = str(post["_id"])
                if withActualUser:
                    post["user"] = await find_user_by_id(post["user_id"])
                post["comments"] = await CommentBase.find_by_post_id(
                    post["id"]
                )
                all_posts.append(PostResponse(**post))
            return all_posts
        return []

    @classmethod
    async def search_posts(cls, keyword):
        resp = []
        posts = await db.posts.find(
            {
                "$text": {
                    "$search": keyword
                }
            }).to_list(None)
        for post in posts:
            post["id"] = str(post["_id"])
            post["user"] = await find_user_by_id(post["user_id"])
            post["comments"] = await CommentBase.find_by_post_id(post["id"])
            resp.append(PostResponseWithUser(**post))
        return resp

    async def add_comment(self, comment_id: str, user_id: str):
        self.comment_ids.append(comment_id)
        done = await db.users.update_one({"_id": ObjectId(user_id)},
                                         {"$set": {
                                             "comment_ids": self.comment_ids
                                         }})
        return done

    async def insert(self):
        row = await db.posts.insert_one(self.dict())
        if row.acknowledged:
            await db.posts.create_index([
                ("text", pymongo.TEXT),
                ("title", pymongo.TEXT)
            ])
            return row.inserted_id
        return None
