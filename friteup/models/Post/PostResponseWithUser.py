from models.Post.PostResponse import PostResponse
from models.User.UserResponse import UserResponse


class PostResponseWithUser(PostResponse):
    user: UserResponse
