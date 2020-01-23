from bson import ObjectId
from pydantic import BaseModel
from typing import List, Any
from models.comment import CommentBase, CommentResponse
from db import db


class PostResponse(BaseModel):
    id: str
    text: str
    title: str
    user_id: str
    createdAt: float
    published: bool
    comments: List[CommentResponse]


class PostBase(BaseModel):
    text: str
    title: str
    user_id: str
    createdAt: float
    published: bool
    comment_ids: List[str] = []

    def add_new_comment(self, comment_id):
        self.comment_ids.insert(comment_id)

    @classmethod
    async def find_by_id(cls, _id):
        post = await db.posts.find_one({"_id": ObjectId(_id)})
        if post:
            post["id"] = str(post["_id"])
            post["comments"] = await CommentBase.find_by_post_id(post["id"])
            return PostResponse(**post)
        return None

    @classmethod
    async def find_by_user_id(cls, user_id):
        posts_count = await db.posts.count_documents({"user_id": user_id})
        posts = await db.posts.find({"user_id": user_id}).to_list(posts_count)
        if posts:
            all_posts = []
            for post in posts:
                post["id"] = str(post["_id"])
                post["comments"] = await CommentBase.find_by_post_id(post["id"])
                all_posts.append(PostResponse(**post))
            return all_posts
        return []

    async def add_comment(self, comment_id: str, user_id: str):
        self.comment_ids.append(comment_id)
        done = await db.users.update_one({"_id": ObjectId(user_id)},
                                         {"$set": {"comment_ids": self.comment_ids}})
        return done

    async def insert(self):
        row = await db.posts.insert_one(self.dict())
        if row.acknowledged:
            return row.inserted_id
        return None


class PostUpdates(BaseModel):
    id: str
    text: str
    title: str
    user_id: str
    published: bool
    comment_ids: List[str] = []

    @classmethod
    async def find_by_id(cls, _id: str):
        post = await db.posts.find_one({"_id": ObjectId(_id)})
        if post:
            post["id"] = str(post["_id"])
            return PostUpdates(**post)
        return None

    @classmethod
    async def find_by_user_id(cls, user_id):
        posts_count = await db.posts.count_documents({"user_id": user_id})
        posts = await db.posts.find({"user_id": user_id}).to_list(posts_count)
        if posts:
            all_posts = []
            for post in posts:
                post["id"] = str(post["_id"])
                post["comments"] = await CommentBase.find_by_post_id(post["id"])
                all_posts.append(PostUpdates(**post))
            return all_posts
        return []

    async def add_comment(self, comment_id: str):
        self.comment_ids.append(comment_id)
        done = await db.posts.update_one({"_id": ObjectId(self.id)},
                                         {"$set": {"comment_ids": self.comment_ids}})
        return done

    async def delete(self):
        await CommentBase.delete_all_comments_for_post(self.id)
        done = await db.posts.delete_one({"_id": self.id})
        return done.acknowledged

    @classmethod
    async def delete_all_posts_for_user(cls, user_id):
        done = db.posts.delete_many({"user_id": user_id})
        return done.acknowledged
