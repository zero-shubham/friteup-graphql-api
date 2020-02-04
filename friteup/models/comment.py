from bson import ObjectId
from pydantic import BaseModel
from db import db


class CommentResponse(BaseModel):
    id: str
    text: str
    user_id: str
    post_id: str


class CommentBase(BaseModel):
    text: str
    user_id: str
    post_id: str

    @classmethod
    async def find_by_id(cls, _id):
        comment = await db.comments.find_one({"_id": ObjectId(_id)})
        if comment:
            comment["id"] = str(comment["_id"])
            return CommentResponse(**comment)
        return None

    @classmethod
    async def find_by_post_id(cls, post_id):
        comments_count = await db.comments.count_documents({"post_id": post_id})
        comments = await db.comments.find({"post_id": post_id}).to_list(comments_count)
        all_comments = []
        if comments:
            for comment in comments:
                comment["id"] = str(comment["_id"])
                all_comments.append(CommentResponse(**comment))
        return all_comments

    @classmethod
    async def find_by_user_id(cls, user_id):
        comments_count = await db.comments.count_documents({"user_id": user_id})
        comments = await db.comments.find({"user_id": user_id}).to_list(comments_count)
        all_comments = []
        if comments:
            for comment in comments:
                comment["id"] = str(comment["_id"])
                all_comments.append(CommentResponse(**comment))
        return all_comments

    async def insert(self):
        row = await db.comments.insert_one(self.dict())
        if row.acknowledged:
            return row.inserted_id
        return None

    @classmethod
    async def delete(cls, comment_id: str):
        done = await db.comments.delete_one({"_id": ObjectId(comment_id)})
        return done.acknowledged

    @classmethod
    async def delete_all_comments_for_user(cls, user_id):
        done = await db.comments.delete_many({"user_id": user_id})
        return done.acknowledged

    @classmethod
    async def delete_all_comments_for_post(cls, post_id):
        done = await db.comments.delete_many({"post_id": post_id})
        return done.acknowledged
