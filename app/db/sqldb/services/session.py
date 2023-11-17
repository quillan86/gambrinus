from typing import Optional
from .generic import SQLService, sql_check
from ..schema import Response, Session as SessionTable
from ....services.llm import truncate_conversation
from sqlalchemy.orm import Session
from langchain.schema import (
    AIMessage,
    HumanMessage,
    BaseMessage
)


class SessionService(SQLService):
    model = SessionTable

    def __init__(self, session: Session):
        super().__init__(session)

    @sql_check
    def create_response(self, session_id: int, human_created_at, question: str, answer: str, intent: str, sources: str) -> int:
        obj = Response(session_id=session_id, human_created_at=human_created_at, human_updated_at=human_created_at, question=question, answer=answer, intent=intent, sources=sources)
        self.insert(obj)
        self.session.refresh(obj)
        return obj

    @sql_check
    def get_session_history(self, session_id: int) -> list[BaseMessage]:
        responses = (self.session.query(Response)
                     .join(self.model)
                     .filter(Response.session_id == session_id)
                     .order_by(Response.human_created_at.asc())
                     .all()
                    )
        result: list[BaseMessage] = []
        for response in responses:
            question = HumanMessage(content=response.question)
            answer = AIMessage(content=response.answer)
            result.extend([question, answer])
        result = truncate_conversation(result)
        if result is None:
            return []
        return result

    @sql_check
    def get_by_user_id(self, user_id: int):
        query = (self.session.query(self.model)
                 .filter(self.model.user_id == user_id)
                 .order_by(self.model.created_at.asc())
                 .all()
                 )
        result = [self.row2dict(x) for x in query]
        print(result)
        return result

