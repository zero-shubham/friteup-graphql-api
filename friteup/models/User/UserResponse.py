from pydantic import BaseModel
from typing import Any, List
from db import db
from bson import ObjectId

import utils.model_utils.user as UserUtils
from models.Post.PostResponse import PostResponse


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    night_mode: bool
    bio: str = ""
    subscribers: List[str] = []
    subscribed: List[str] = []
    posts: List[PostResponse]

    async def get_feed(self):
        posts = []
        for subscribed_user_id in self.subscribed:
            subscribed_user = await UserUtils.find_user_by_id(subscribed_user_id, False)
            subscribed_user = UserResponse(**subscribed_user)
            posts.append(subscribed_user.posts)
        posts = sorted(posts, key=lambda i: i["created_at"])
        return posts
