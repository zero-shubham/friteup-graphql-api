import os
import uvicorn
from fastapi import FastAPI
from ariadne import make_executable_schema
from ariadne.asgi import GraphQL
from starlette.requests import Request
from starlette.responses import JSONResponse
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
    "http://localhost:8000"
]


app = FastAPI()
app.mount("/graphql", GraphQL(schema, debug=True))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=[
        "Accept",
        "Accept-Encoding",
        "Authorization",
        "Content-Type",
        "Origin",
        "User-Agent"
    ]
)
app.add_middleware(
    AuthenticationMiddleware,
    backend=BasicAuthBackend()
)


@app.middleware("http")
async def cookie_set(request: Request, call_next):
    response = await call_next(request)
    del_cookie_flag = False
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
            del_cookie_flag = True
    else:
        del_cookie_flag = True

    if del_cookie_flag:
        response.delete_cookie(
            key="Authorization",
            path="/",
            domain=None
        )

    await token_db.remove_token(request.user.req_id)
    return response

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run("application:app", host="0.0.0.0", port=port, log_level="info")
