from typing import List, Optional
from sqlalchemy import Boolean, Integer, String, Text, ForeignKey, Table, Column, DateTime, func, DECIMAL, Numeric, NVARCHAR
from sqlalchemy.types import UnicodeText
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column, Mapped, relationship
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from . import engine

# https://stackoverflow.com/questions/53704187/connecting-to-an-azure-database-using-sqlalchemy-in-python


class Base(DeclarativeBase):
    pass


# association table
user_permission = Table("user_permission",
                        Base.metadata,
                        Column("user_id", ForeignKey("user.id", ondelete="CASCADE"), primary_key=True),
                        Column("permission_id", ForeignKey("permission.id", ondelete="CASCADE"), primary_key=True),
                        )
user_group = Table("user_group",
                   Base.metadata,
                   Column("user_id", ForeignKey("user.id", ondelete="CASCADE"), primary_key=True),
                   Column("group_id", ForeignKey("group.id", ondelete="CASCADE"), primary_key=True),
                   )
group_permission = Table("group_permission",
                         Base.metadata,
                         Column("group_id", ForeignKey("group.id", ondelete="CASCADE"), primary_key=True),
                         Column("permission_id", ForeignKey("permission.id", ondelete="CASCADE"), primary_key=True),
                         )


class Client(Base):
    __tablename__ = "client"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), insert_default=func.now())
    description: Mapped[str] = mapped_column(UnicodeText, nullable=True)
    logo: Mapped[str] = mapped_column(String(250), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)


    users: Mapped[List["User"]] = relationship(back_populates="client", cascade="all, delete", passive_deletes=True)
    address: Mapped["Address"] = relationship(back_populates="client", cascade="all, delete", passive_deletes=True, uselist=False)

    def __str__(self):
        return f"Client ({self.id})"


class Address(Base):
    __tablename__ = "address"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_id: Mapped[int] = mapped_column(Integer, ForeignKey("client.id"), nullable=False)
    street: Mapped[Optional[str]] = mapped_column(String(250), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    zip_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Numeric(precision=9, scale=6), nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Numeric(precision=9, scale=6), nullable=True)

    client: Mapped["Client"] = relationship(back_populates="address")

    def __str__(self):
        return f"Address ({self.id})"


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), insert_default=func.now())
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    photo: Mapped[Optional[str]] = mapped_column(String(250), nullable=True)
    title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    client_id: Mapped[int] = mapped_column(Integer, ForeignKey("client.id", ondelete="CASCADE"), nullable=True)


    permissions: Mapped[List["Permission"]] = relationship(secondary=user_permission, back_populates='users', cascade="all, delete")
    groups: Mapped[List["Group"]] = relationship(secondary=user_group, back_populates='users', cascade="all, delete")
    sessions: Mapped[List["Session"]] = relationship(back_populates="user", cascade="all, delete", passive_deletes=True)
    client: Mapped[List["Client"]] = relationship(back_populates="users")
    custom_messages: Mapped[List["CustomMessage"]] = relationship(back_populates="user", cascade="all, delete", passive_deletes=True)
    cookies: Mapped[List["Cookie"]] = relationship(back_populates="user", cascade="all, delete", passive_deletes=True)


    def __str__(self):
        return f"User ({self.id})"


class Permission(Base):
    __tablename__ = "permission"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False) # visual name
    description: Mapped[str] = mapped_column(String(), nullable=False)

    users: Mapped[List["User"]] = relationship(secondary=user_permission, back_populates='permissions', passive_deletes=True)
    groups: Mapped[List["Group"]] = relationship(secondary=group_permission, back_populates='permissions', passive_deletes=True)

    def __str__(self):
        return f"Permission ({self.id})"


class Group(Base):
    __tablename__ = "group"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False) # visual name
    description: Mapped[str] = mapped_column(String(), nullable=False)

    users: Mapped[List["User"]] = relationship(secondary=user_group, back_populates='groups', passive_deletes=True)
    permissions: Mapped[List["Permission"]] = relationship(secondary=group_permission, back_populates='groups', passive_deletes=True)

    def __str__(self):
        return f"Group ({self.id})"


class CustomQuestion(Base):
    __tablename__ = "custom_question"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question: Mapped[str] = mapped_column(UnicodeText, nullable=False)
    prompt: Mapped[str] = mapped_column(UnicodeText, nullable=False)

    custom_messages: Mapped[List["CustomMessage"]] = relationship(back_populates="custom_question", cascade="all, delete", passive_deletes=True)

    def __str__(self):
        return f"Custom Question ({self.id})"


class CustomMessage(Base):
    __tablename__ = "custom_message"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    custom_question_id: Mapped[int] = mapped_column(Integer, ForeignKey("custom_question.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    message: Mapped[str] = mapped_column(UnicodeText, nullable=False)

    custom_question: Mapped["CustomQuestion"] = relationship(back_populates="custom_messages")
    user: Mapped["User"] = relationship(back_populates="custom_messages")

    def __str__(self):
        return f"Custom Message ({self.id})"


class Session(Base):
    __tablename__ = "session"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), insert_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), insert_default=func.now())
    name: Mapped[str] = mapped_column(String(250)) # name of session

    responses: Mapped[List["Response"]] = relationship(back_populates="session", cascade="all, delete")
    user: Mapped["User"] = relationship(back_populates="sessions")

    def __str__(self):
        return f"Session ({self.id})"


class Response(Base):
    __tablename__ = "response"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("session.id", ondelete="CASCADE"))
    human_created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), insert_default=func.now())
    human_updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), insert_default=func.now())
    assistant_created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), insert_default=func.now())
    assistant_updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), insert_default=func.now())
    question: Mapped[str] = mapped_column(UnicodeText, nullable=False)
    answer: Mapped[str] = mapped_column(UnicodeText, nullable=False)
    intent: Mapped[str] = mapped_column(String(50), nullable=False)
    sources: Mapped[str] = mapped_column(UnicodeText, nullable=True)
    # positive, negative, or null
    feedback_check: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    # category of feedback - such as wrong intent or not helpful response
    feedback_category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    # freehand comment for feedback
    feedback_comment: Mapped[Optional[str]] = mapped_column(UnicodeText, nullable=True)

    session: Mapped["Session"] = relationship(back_populates="responses")

    def __str__(self):
        return f"Response ({self.id})"


class Cookie(Base):
    __tablename__ = 'cookie'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    token: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), insert_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), insert_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)

    user: Mapped["User"] = relationship(back_populates="cookies")

class Contact(Base):
    __tablename__ = 'contact'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(UnicodeText, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), insert_default=func.now())


def reset_schema():
    if len(Base.metadata.tables.keys()) > 0:
        print("Dropping all tables...")
        Base.metadata.drop_all(bind=engine)

    # Create all the tables in the database which are
    # defined by Base's subclasses such as User
    print("Creating tables...")
    Base.metadata.create_all(engine)

    # Construct a sessionmaker factory object
    session = sessionmaker()
    # Bind the sessionmaker to engine
    session.configure(bind=engine)

    # Generate a session to work with
    s = session()
    s.commit()
    s.close()
