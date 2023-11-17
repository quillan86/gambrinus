from typing import Optional
from .generic import SQLService, sql_check
from ..schema import Cookie
from sqlalchemy.orm import Session


class CookieService(SQLService):
    model = Cookie

    def __init__(self, session: Session):
        super().__init__(session)

    @sql_check
    def get_by_token(self, token: str) -> Optional[Cookie]:
        return self.session.query(self.model).filter(self.model.token == token).one_or_none()
