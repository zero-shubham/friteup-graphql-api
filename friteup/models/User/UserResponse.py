from pydantic import BaseModel
from typing import Any, List
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
