from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Client(BaseModel):
    id: int
    name: str
    description: Optional[str]
    logo: Optional[str]
    photo: Optional[str]


class User(BaseModel):
    id: int
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    photo: Optional[str]
    title: Optional[str]
    client_id: Optional[int]
    created_at: datetime


class Case(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime
    closed_at: datetime
