from pydantic import BaseModel
from typing import List, Any
from models.comment import CommentResponse


class PostResponse(BaseModel):
    id: str
    text: str
    title: str
    user_id: str
    created_at: float
    published: bool
    up_vote: List[str]
    down_vote: List[str]
    comments: List[CommentResponse]
