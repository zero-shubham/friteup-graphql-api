from pydantic import BaseModel
from bson import ObjectId
from db import db
from typing import Any, List
from models.comment import CommentBase


class PostUpdates(BaseModel):
    id: str
    text: str
    title: str
    user_id: str
    published: bool
    up_vote: List[str]
    down_vote: List[str]
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

                post["comments"] = await CommentBase.find_by_post_id(
                    post["id"]
                )
                all_posts.append(PostUpdates(**post))
            return all_posts
        return []

    async def add_comment(self, comment_id: str):
        self.comment_ids.append(comment_id)
        done = await db.posts.update_one({"_id": ObjectId(self.id)},
                                         {"$set": {
                                             "comment_ids": self.comment_ids
                                         }})
        return done

    async def delete(self):
        await CommentBase.delete_all_comments_for_post(self.id)
        done = await db.posts.delete_one({"_id": self.id})
        return done.acknowledged

    async def vote(self, vote_type, user_id):
        if vote_type == "UP_VOTE":
            if user_id in self.up_vote:
                self.up_vote.remove(user_id)
            else:
                if user_id in self.down_vote:
                    self.down_vote.remove(user_id)
                self.up_vote.append(user_id)
        elif vote_type == "DOWN_VOTE":
            if user_id in self.down_vote:
                self.down_vote.remove(user_id)
            else:
                if user_id in self.up_vote:
                    self.up_vote.remove(user_id)
                self.down_vote.append(user_id)
        done = await db.posts.update_one(
            {"_id": ObjectId(self.id)},
            {"$set": {"up_vote": self.up_vote, "down_vote": self.down_vote}}
        )
        return done.acknowledged

    @classmethod
    async def delete_all_posts_for_user(cls, user_id):
        done = db.posts.delete_many({"user_id": user_id})
        return done.acknowledged
