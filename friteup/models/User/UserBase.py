from pydantic import BaseModel
from typing import List


class UserBase(BaseModel):
    name: str
    password: str
    email: str
    night_mode: bool = False
    bio: str = ""
    subscribers: List[str] = []
    subscribed: List[str] = []
    post_ids: List[str] = []
    comment_ids: List[str] = []
