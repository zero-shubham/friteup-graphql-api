import jwt
import uuid
import datetime
from starlette.requests import Request
from starlette.authentication import (
    AuthenticationBackend, AuthCredentials, BaseUser
)
from models import token
from models.token import TokenBase
from utils.MyErrors import GenericError
from utils.token_db import token_db


def authentication_required(resolver):
    async def wrapper_func(source, info, **kwargs):
        request = info.context["request"]
        result = None
        # allow to run the resolver only if request is authenticated
        # todo: else should throw error
        if request.user.is_authenticated:
            kwargs["current_user_id"] = request.user.current_user_id
            result = await resolver(source, info, **kwargs)
        return result

    return wrapper_func


async def check_user_in_db(user_id: str, received_token: str):
    token_in_db = await TokenBase.find_by_user_id(user_id)
    if token_in_db and token_in_db["token"] == received_token:
        return True
    return False


class AuthenticatedUser(BaseUser):
    def __init__(self, user_id: str = None, expires: float = 0.0):
        self.current_user_id = user_id
        self.expires = expires
        self.req_id = uuid.uuid4().hex

    @property
    def is_authenticated(self) -> bool:
        return True


class UnAuthenticatedUser(BaseUser):
    def __init__(self):
        self.req_id = uuid.uuid4().hex

    @property
    def is_authenticated(self) -> bool:
        return False


# authenticates each request and provides an unique reuest id to each
class BasicAuthBackend(AuthenticationBackend):
    async def authenticate(self, request):
        ret_value = None
        if "Authorization" in request.cookies.keys() and request.cookies["Authorization"]:
            token = request.cookies["Authorization"].encode()
            decoded_token = jwt.decode(token, "secret", algorithms=['HS256'])
            match_token = await check_user_in_db(decoded_token["id"], token.decode())
            now = datetime.datetime.now()
            if match_token and now.timestamp() < decoded_token["expire"]:
                ret_value = AuthenticatedUser(
                    user_id=decoded_token["id"], expires=decoded_token["expire"]
                )
                await token_db.set_token(
                    ret_value.req_id,
                    token,
                    decoded_token["expire"]
                )
            else:
                ret_value = UnAuthenticatedUser()

        else:
            ret_value = UnAuthenticatedUser()
        return AuthCredentials(["authenticated"]), ret_value
