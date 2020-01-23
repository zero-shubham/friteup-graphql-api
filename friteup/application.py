from fastapi import FastAPI
from ariadne import make_executable_schema
from ariadne.asgi import GraphQL
from starlette.requests import Request
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware
from middlewares.authentication import BasicAuthBackend
from utils.token_db import token_db
from resolvers.user import user_query, user_mutation, User
from resolvers.post import post_query, post_mutation, Post
from resolvers.comment import comment_query, comment_mutation
from schemas.schema import type_defs
import uuid

schema = make_executable_schema(type_defs, [
    user_query,
    user_mutation,
    User,
    post_query,
    post_mutation,
    Post,
    comment_query,
    comment_mutation
]
)

origins = [
    "http://localhost",
    "http://localhost:8000",
]

app = FastAPI()
app.mount("/graphql", GraphQL(schema, debug=True))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    AuthenticationMiddleware,
    backend=BasicAuthBackend()
)


@app.middleware("http")
async def cookie_set(request: Request, call_next):
    response = await call_next(request)
    if request.user.req_id in token_db.db.keys():
        token = token_db.db[request.user.req_id]
        if token["valid"]:
            response.set_cookie(
                key="Authorization",
                value=token["access_token"].decode("utf-8"),
                expires=int(token["expires"]),
                httponly=True
            )
        else:
            response.delete_cookie(key="Authorization", path="/", domain=None)
            token_db.remove_token(request.user.req_id)
    return response
