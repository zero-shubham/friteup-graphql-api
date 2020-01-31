from pydantic import BaseModel
from typing import List, Any
from models.comment import CommentResponse


class PostResponse(BaseModel):
    id: str
    text: str
    title: str
    user_id: str
    createdAt: float
    published: bool
    up_vote: int
    down_vote: int
    comments: List[CommentResponse]
