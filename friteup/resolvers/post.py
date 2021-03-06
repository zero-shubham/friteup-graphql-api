from ariadne import ObjectType, QueryType, MutationType
import datetime

import utils.model_utils.post as PostUtils
from models.comment import CommentBase
from models.Post.PostBase import PostResponse, PostBase
from models.Post.PostUpdates import PostUpdates
from models.User.UserInDB import UserInDB
from models.User.UserUpdates import UserUpdates
from middlewares.authentication import authentication_required

post_query = QueryType()
post_mutation = MutationType()
Post = ObjectType("Post")


@post_query.field("post")
@authentication_required
async def resolve_post(_, info, **kwargs):
    request = info.context["request"]
    current_user_id = kwargs.get("current_user_id", None)
    user_id = kwargs.get("user_id", None)
    post_id = kwargs.get("post_id", None)
    post = None
    is_auth = request.user.is_authenticated and current_user_id == user_id
    if post_id:
        post = [await PostUtils.find_posts_by_id(post_id, is_auth)]
    elif user_id:
        post = await PostUtils.find_posts_by_user_id(user_id, is_auth)
    return post


@post_mutation.field("create_post")
@authentication_required
async def resolve_create_post(_, info, **kwargs):
    user_id = kwargs.get("current_user_id", None)
    text = kwargs.get("text", None)
    title = kwargs.get("title", None)
    published = kwargs.get("published", False)
    post_created = None
    if user_id and text and title:
        user = await UserUpdates.find_by_id(user_id)
        if user:
            now = datetime.datetime.now()
            new_post = PostBase(
                user_id=user_id,
                text=text,
                created_at=now.timestamp(),
                title=title,
                published=published
            )
            new_post_id = await new_post.insert()
            await user.add_post(new_post_id)
            new_post = new_post.dict()
            new_post["id"] = str(new_post_id)
            new_post["comments"] = await CommentBase.find_by_post_id(new_post_id)
            post_created = PostResponse(**new_post)
    return post_created


@post_mutation.field("delete_post")
@authentication_required
async def resolve_delete_post(_, info, **kwargs):
    user_id = kwargs.get("current_user_id", None)
    post_id = kwargs.get("post_id", None)
    post = None
    done = False
    # error handling if both are not true
    if user_id and post_id:
        post = await PostUpdates.find_by_id(post_id)
        # error handling if both are not same
        if post.user_id == user_id:
            done = await post.delete()
            done = done.acknowledge
    if done:
        return post


@post_mutation.field("vote_post")
@authentication_required
async def resolve_vote_post(_, info, **kwargs):
    current_user_id = kwargs.get("current_user_id", None)
    post_id = kwargs.get("post_id", None)
    vote_type = kwargs.get("vote_type", None)
    post = await PostUpdates.find_by_id(_id=post_id)
    done = False
    if post and vote_type:
        done = await post.vote(vote_type, current_user_id)
    if done:
        updated_post = await PostUtils.find_posts_by_id(post_id, False, True)
    return updated_post


@Post.field("comments")
async def resolve_comments(root, info):
    return root.comments
