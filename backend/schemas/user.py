from pydantic import BaseModel


class UserResponse(BaseModel):
    id: int
    name: str
    embedding_count: int


class UserCreateResponse(UserResponse):
    message: str
