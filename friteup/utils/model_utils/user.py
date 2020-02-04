from bson import ObjectId

import utils.model_utils.post as PostUtils
from models.User.UserResponse import UserResponse
from db.mongodb import get_database


async def find_user_by_email(email, is_authenticated):
    db = await get_database()
    user = await db.users.find_one({"email": email})
    if user:
        user["id"] = str(user["_id"])
        user["posts"] = await PostUtils.find_posts_by_user_id(
            user_id=user["id"],
            is_authenticated=is_authenticated
        )
        return UserResponse(**user)
    return None


async def find_user_by_id(_id, is_authenticated, posts=True):
    db = await get_database()
    user = await db.users.find_one({"_id": ObjectId(_id)})
    if user:
        user["id"] = str(user["_id"])
        user["posts"] = []
        if posts:
            user["posts"] = await PostUtils.find_posts_by_user_id(
                user_id=user["id"],
                is_authenticated=is_authenticated,
                with_user=True
            )
        return UserResponse(**user)
    return None
