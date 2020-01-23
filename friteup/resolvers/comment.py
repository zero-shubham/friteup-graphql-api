from ariadne import ObjectType, QueryType, MutationType

from models.comment import CommentBase
from models.post import PostUpdates
from models.user import UserUpdates
from middlewares.authentication import authentication_required

comment_query = QueryType()
comment_mutation = MutationType()


@comment_query.field("comment")
@authentication_required
async def resolve_comment(_, info, **kwargs):
    post_id = kwargs.get("post_id", None)
    user_id = kwargs.get("user_id", None)
    comment_id = kwargs.get("comment_id", None)
    comment = None
    if comment_id:
        comment = await CommentBase.find_by_id(comment_id)
    elif post_id:
        comment = await CommentBase.find_by_post_id(post_id)
    elif user_id:
        comment = await CommentBase.find_by_user_id(user_id)
    return comment


@comment_mutation.field("create_comment")
@authentication_required
async def resolve_create_comment(_, info, **kwargs):
    user_id = kwargs.get("current_user_id", None)
    post_id = kwargs.get("post_id", None)
    text = kwargs.get("text", None)
    comment = None
    post = await PostUpdates.find_by_id(post_id)
    if user_id and post_id and text and post:
        comment = CommentBase(text=text, user_id=user_id, post_id=post_id)
        new_comment_id = await comment.insert()
        comment = comment.dict()
        comment["id"] = str(new_comment_id)
        user = await UserUpdates.find_by_id(user_id)
        await user.add_comment(comment["id"])
        post = await PostUpdates.find_by_id(post_id)
        await post.add_comment(comment["id"])
    return comment


@comment_mutation.field("delete_comment")
@authentication_required
async def resolve_delete_comment(_, info, **kwargs):
    user_id = kwargs.get("current_user_id", None)
    comment_id = kwargs.get("comment_id", None)
    # error handling
    done = None
    comment = None
    if user_id and comment_id:
        comment = await CommentBase.find_by_id(comment_id)
        if comment.user_id == user_id:
            done = await comment.delete()
    if done:
        return comment
