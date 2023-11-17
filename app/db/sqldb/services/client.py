from typing import Optional
from .generic import SQLService, sql_check
from ..schema import User, Client, CustomMessage, CustomQuestion, Session as SessionTable
from sqlalchemy import or_
from sqlalchemy.orm import Session


class ClientService(SQLService):
    model = Client

    def __init__(self, session: Session):
        super().__init__(session)


