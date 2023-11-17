from typing import Optional
from .generic import SQLService, sql_check
from ..schema import Contact
from sqlalchemy.orm import Session


class ContactService(SQLService):
    model = Contact

    def __init__(self, session: Session):
        super().__init__(session)

