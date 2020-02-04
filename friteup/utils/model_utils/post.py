from bson import ObjectId

from models.Post.PostResponse import PostResponse
from models.Post.PostResponseWithUser import PostResponseWithUser
from models.comment import CommentBase
import utils.model_utils.user as UserUtils
from db.mongodb import get_database


async def find_posts_by_id(_id, is_authenticated, with_user=False):
    db = await get_database()
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
        if with_user:
            post["user"] = await UserUtils.find_user_by_id(
                _id=post["user_id"],
                is_authenticated=False,
                posts=False
            )
        post["comments"] = await CommentBase.find_by_post_id(post["id"])
        if with_user:
            return PostResponseWithUser(**post)
        return PostResponse(**post)
    return None


async def find_posts_by_user_id(
    user_id,
    is_authenticated,
    with_user=False
):
    db = await get_database()
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
            if with_user:
                post["user"] = await UserUtils.find_user_by_id(
                    post["user_id"],
                    False,
                    False
                )
            post["comments"] = await CommentBase.find_by_post_id(
                post["id"]
            )
            if with_user:
                all_posts.append(PostResponseWithUser(**post))
            else:
                all_posts.append(PostResponse(**post))
        return all_posts
    return []
