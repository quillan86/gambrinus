from sqlalchemy.orm import sessionmaker
from .. import engine
from .user import UserService
from .session import SessionService
from .response import ResponseService
from .client import ClientService
from .contact import ContactService
from .cookie import CookieService

session_maker = sessionmaker()
session_maker.configure(bind=engine)

session = session_maker()

client_service = ClientService(session)
user_service = UserService(session)
session_service = SessionService(session)
response_service = ResponseService(session)
contact_service = ContactService(session)
cookie_service = CookieService(session)

__all__ = ['session_service', 'user_service', 'response_service', 'client_service', 'contact_service']
