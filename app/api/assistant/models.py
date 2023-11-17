from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ResponseAndFeedback(BaseModel):
    session_id: str
    human_created_at: datetime
    human_updated_at: datetime
    assistant_created_at: datetime
    assistant_updated_at: datetime
    question: str
    answer: str
    intent: str
    sources: Optional[str]
    feedback_check: Optional[bool]
    feedback_category: Optional[str]
    feedback_comment: Optional[str]


class Response(BaseModel):
    id: int
    human_created_at: datetime
    assistant_created_at: datetime
    answer: str
    sources: Optional[str]
    intent: str


class Feedback(BaseModel):
    session_id: str
    question: str
    answer: str
    intent: str
    feedback_check: Optional[bool]
    feedback_category: Optional[str]
    feedback_comment: Optional[str]


class FullResponse(BaseModel):
    id: int
    session_id: int
    human_created_at: datetime
    human_updated_at: datetime
    assistant_created_at: datetime
    assistant_updated_at: datetime
    question: str
    answer: str
    intent: str
    sources: Optional[str]
    feedback_check: Optional[bool]
    feedback_category: Optional[str]
    feedback_comment: Optional[str]


class Session(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    name: str


class SessionSummary(BaseModel):
    summary: str
