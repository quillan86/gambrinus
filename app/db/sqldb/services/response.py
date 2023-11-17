from typing import Optional
from .generic import SQLService, sql_check
from ..schema import Response, Session as SessionTable
from sqlalchemy.orm import Session


class ResponseService(SQLService):
    model = Response

    def __init__(self, session: Session):
        super().__init__(session)

    @sql_check
    def get_by_session(self, session_id: int):
        query = (self.session.query(self.model)
                 .filter(self.model.session_id == session_id)
                 .order_by(self.model.human_created_at.asc())
                 .all()
                 )
        result = [self.row2dict(x) for x in query]
        return result

    @sql_check
    def get_last_intent(self, session_id: int) -> Optional[str]:
        response = (self.session.query(self.model)
                     .filter(self.model.session_id == session_id)
                     .order_by(self.model.human_created_at.desc())
                     .first()
                    )
        result = response.intent
        return result
