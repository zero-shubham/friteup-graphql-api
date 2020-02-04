import asyncio
from ariadne import QueryType, MutationType, ObjectType, SubscriptionType
import jwt
from starlette.requests import Request
import datetime
from starlette.config import Config

from middlewares.authentication import authentication_required
import utils.model_utils.user as UserUtils
from models.comment import CommentBase
from models.Post.PostBase import PostBase
from models.Post.PostUpdates import PostUpdates
from models.User.UserInDB import UserInDB
from models.User.UserUpdates import UserUpdates
from models.User.UserResponse import UserResponse
from models.token import TokenBase
from utils.MyErrors import GenericError
from utils.token_db import token_db
from db import db


config = Config('.env')

user_query = QueryType()
user_mutation = MutationType()
# user_subscription = SubscriptionType()
User = ObjectType("User")
# queue = asyncio.Queue()
# event = asyncio.Event()


@user_query.field("user")
@authentication_required
async def resolve_user(_, info, **kwargs):
    request = info.context["request"]
    current_user_id = kwargs.get("current_user_id", None)
    user_id = kwargs.get("user_id", None)
    email = kwargs.get("email", None)
    user = None
    authenticated = (request.user.is_authenticated
                     and
                     current_user_id == user_id)
    if email:
        user = await UserUtils.find_user_by_email(
            email,
            authenticated
        )
    elif user_id:
        user = await UserUtils.find_user_by_id(
            user_id,
            authenticated
        )
    return user


@user_query.field("users")
@authentication_required
async def resolve_users(_, info, **kwargs):
    user_ids = kwargs.get("user_ids", None)
    emails = kwargs.get("emails", None)
    users = None
    if user_ids:
        users = [await UserUtils.find_user_by_id(user_id, False) for user_id in user_ids]
    elif emails:
        users = [await UserUtils.find_user_by_email(email, False) for email in emails]
    return users


@user_query.field("user_validate")
@authentication_required
async def resolve_validate_user(_, info, **kwargs):
    request = info.context["request"]
    current_user_id = kwargs.get("current_user_id", None)
    user_id = kwargs.get("user_id", None)
    response = {
        "user_id": user_id,
        "valid": False
    }
    if user_id and current_user_id and user_id == current_user_id:
        user = await UserUtils.find_user_by_id(
            _id=current_user_id,
            is_authenticated=request.user.is_authenticated
        )
        user = user.dict()
        if user["id"] == user_id:
            response["valid"] = True
    return response


@user_query.field("search")
@authentication_required
async def resolve_search(_, info, **kwargs):
    keyword = kwargs.get("keyword", None)
    current_user_id = kwargs.get("current_user_id", None)
    resp = {
        "users": [],
        "posts": []
    }
    if keyword:
        resp["users"] = await UserInDB.search_users(keyword, current_user_id)
        resp["posts"] = await PostBase.search_posts(keyword)
    return resp


@user_query.field("feed")
@authentication_required
async def resolve_feed(_, info, **kwargs):
    current_user_id = kwargs.get("current_user_id", None)
    request = info.context["request"]
    user = await UserUtils.find_user_by_id(
        _id=current_user_id,
        is_authenticated=request.user.is_authenticated
    )
    resp = []
    if user:
        resp = await user.get_feed()
    return resp


@user_mutation.field("create_user")
async def resolve_create_user(_, info, data):
    if await UserUtils.find_user_by_email(data["email"], False):
        raise GenericError("User with that e-mail already exists!")
    user = UserInDB(name=data["name"],
                    email=data["email"], password=data["password"])

    inserted_user_id = await user.insert()
    if not inserted_user_id:
        raise GenericError("Something went wrong!")
    user = user.dict()
    user["id"] = str(inserted_user_id)
    user["posts"] = []
    return UserResponse(**user)


@user_mutation.field("login")
async def resolve_login(_, info, email, password):
    request = info.context["request"]
    checked_user = await UserInDB.check_password(
        email,
        password,
        request.user.is_authenticated
    )
    if checked_user:
        now = datetime.datetime.now()
        expires = now + datetime.timedelta(days=3)
        payload = {
            "id": checked_user.id,
            "expire": expires.timestamp()
        }
        access_token = jwt.encode(payload, "secret", algorithm='HS256')
        await TokenBase.delete(checked_user.id)
        token_in_db = TokenBase(user_id=checked_user.id, token=access_token)
        await token_in_db.insert()
        expires_in_seconds = expires.timestamp() - now.timestamp()
        await token_db.set_token(
            request.user.req_id,
            access_token,
            expires_in_seconds
        )
        return {"user": checked_user}


@user_mutation.field("logout")
@authentication_required
async def resolve_logout(_, info, **kwargs):
    response = {
        "logged_out": False
    }
    current_user_id = kwargs.get("current_user_id", None)
    request = info.context["request"]
    if request.user.is_authenticated and current_user_id:
        deleted = await TokenBase.delete(current_user_id)
        if deleted:
            await token_db.invalidate_token(request.user.req_id)
            response["logged_out"] = True
    return response


@user_mutation.field("delete_user")
@authentication_required
async def resolve_delete_user(_, info, **kwargs):
    user_id = kwargs.get("current_user_id", None)
    result = False
    if user_id:
        user = await UserUpdates.find_by_id(user_id)
        if user:
            # error handling
            await PostUpdates.delete_all_posts_for_user(user_id)
            await CommentBase.delete_all_comments_for_user(user_id)
            for subscriber_id in user.subscribers:
                subscriber_user = await UserUpdates.find_by_id(subscriber_id)
                await subscriber_user.remove_subscribed(user_id)
                await user.remove_subscriber(subscriber_id)
            for subscribed_id in user.subscribed:
                subscribed_user = await UserUpdates.find_by_id(subscribed_id)
                await subscribed_user.remove_subscriber(user_id)
                await user.remove_subscribed(subscribed_id)
            done = await user.delete()
            if done:
                result = True
    return result


@user_mutation.field("update_user")
@authentication_required
async def resolve_update_user(_, info, **kwargs):
    user_id = kwargs.get("current_user_id", None)
    update_data = kwargs.get("data", None)
    if user_id and update_data:
        user = await UserUpdates.find_by_id(
            _id=user_id
        )
        allowed_update_details = ["night_mode", "name", "email", "bio"]
        if user and all(
            [key in allowed_update_details for key in update_data.keys()]
        ):
            await user.update_user_details(update_data)
    user_updated = await UserUpdates.find_by_id(
        _id=user_id
    )
    return user_updated


@user_mutation.field("change_password")
@authentication_required
async def resolve_change_password(_, info, **kwargs):
    request = info.context["request"]
    user_id = kwargs.get("current_user_id", None)
    old_password = kwargs.get("old_password", None)
    new_password = kwargs.get("new_password", None)
    if user_id and old_password and new_password:
        user = await UserUpdates.find_by_id(user_id)
        if user:
            match_password = await UserInDB.check_password(
                user.email,
                old_password,
                request.user.is_authenticated
            )
            if match_password:
                done = await user.change_password(new_password)
                return done
    return False


@user_mutation.field("subscribe_user")
@authentication_required
async def resolve_subscribe_user(_, info, **kwargs):
    current_user_id = kwargs.get("current_user_id", None)
    user_id = kwargs.get("user_id", None)
    user = await UserUpdates.find_by_id(user_id)
    current_user = await UserUpdates.find_by_id(current_user_id)
    if user and current_user:
        # already subscribed handle error
        if current_user_id in user.subscribers:
            return False
        # add error handling
        done = await user.add_subscriber(current_user_id)
        if done:
            done = await current_user.add_subscribed(user_id)
    return done


@user_mutation.field("unsubscribe_user")
@authentication_required
async def resolve_unsubscribe_user(_, info, **kwargs):
    current_user_id = kwargs.get("current_user_id", None)
    user_id = kwargs.get("user_id", None)
    user = await UserUpdates.find_by_id(user_id)
    current_user = await UserUpdates.find_by_id(current_user_id)
    if user and current_user:
        # if current_user is not in subscribers list error
        if current_user_id not in user.subscribers:
            return False
        # add error handling
        done = await user.remove_subscriber(current_user_id)
        if done:
            done = await current_user.remove_subscribed(user_id)
    return done


@User.field("posts")
async def resolve_posts(root, info):
    return root.posts


# @user_subscription.source("count")
# async def generate_count(obj, info):
#     while True:
#         c = await event.wait()
#         yield c
#
#
# @user_subscription.field("count")
# async def resolve_count_sub(count: int, info):
#     event.clear()
#     return 1
