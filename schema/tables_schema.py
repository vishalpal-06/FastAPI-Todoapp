
from pydantic import BaseModel, Field
from typing import Optional

class TodoCreateRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: str = Field(default="Low")
    status: str = Field(default="Pending")

class TodoUpdateRequest(BaseModel):
    title: str = Field(min_length=3)
    description: Optional[str] = Field(default=None, min_length=3, max_length=100)
    priority: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None)

class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str















