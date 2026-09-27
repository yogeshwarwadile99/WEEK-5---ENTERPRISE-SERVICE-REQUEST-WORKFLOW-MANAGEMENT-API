from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CommentCreate(BaseModel):
    comment: str
    is_internal: bool = False

class CommentUpdate(BaseModel):
    comment: str

class CommentResponse(BaseModel):
    id: int
    request_id: int
    user_id: int
    comment: str
    is_internal: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CommentUserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str

class CommentWithUserResponse(CommentResponse):
    user: CommentUserResponse