from typing import Optional
from .generic import SQLService, sql_check
from ..schema import User, Client, CustomMessage, CustomQuestion, Session as SessionTable
from ..schema import user_permission, user_group, group_permission, Permission, Group
from sqlalchemy import or_
from sqlalchemy.orm import Session


class UserService(SQLService):
    model = User

    def __init__(self, session: Session):
        super().__init__(session)

    @sql_check
    def get_by_email(self, email: str) -> Optional[User]:
        return self.session.query(self.model).filter(self.model.email == email).one_or_none()

    @sql_check
    def get_permissions(self, user_id: int) -> list[Permission]:
        query = (self.session.query(Permission)
                 .join(user_permission)
                 .join(self.model)
                 .join(group_permission)
                 .join(user_group)
                 .join(Group)
                 .filter(user_permission.c.user_id == user_id)
                 .filter(user_group.c.user_id == user_id)
                 .filter(group_permission.c.group_id == user_group.c.group_id)
                 .filter(or_(Permission.id == user_permission.c.permission_id, Permission.id == group_permission.c.permission_id))
                 .all()
                 )
        return query

    @sql_check
    def get_groups(self, user_id: int) -> list[Group]:
        query = (self.session.query(Group)
                 .join(user_group)
                 .join(self.model)
                 .filter(user_group.c.user_id == user_id)
                 .filter(Group.id == user_group.c.group_id)
                 .all()
                 )
        return query

    @sql_check
    def create_session(self, user_id: int, name: str) -> int:
        obj = SessionTable(user_id=user_id, name=name)
        self.insert(obj)
        self.session.refresh(obj)
        return obj.id

    @sql_check
    def create_permission(self, user_id: int, permission_id: int) -> bool:
        user = self.get_by_id(user_id)
        permission = self.session.query(Permission).filter(Permission.id == permission_id).one_or_none()
        user.permissions.append(permission)
        self.commit()
        return True

    @sql_check
    def delete_permission(self, user_id: int, permission_id: int) -> bool:
        user = self.get_by_id(user_id)
        permission = self.session.query(Permission).filter(Permission.id == permission_id).one_or_none()
        user.permissions.remove(permission)
        self.commit()
        return True

    @sql_check
    def join_group(self, user_id: int, group_id: int) -> bool:
        user = self.get_by_id(user_id)
        group = self.session.query(Group).filter(Permission.id == group_id).one_or_none()
        user.groups.append(group)
        self.commit()
        return True

    @sql_check
    def leave_group(self, user_id: int, group_id: int) -> bool:
        user = self.get_by_id(user_id)
        group = self.session.query(Group).filter(Permission.id == group_id).one_or_none()
        user.groups.remove(group)
        self.commit()
        return True

    @sql_check
    def get_custom_messages(self, user_id: int) -> list[dict]:
        query = (self.session.query(
            CustomMessage.user_id.label("user_id"),
            CustomQuestion.question.label("question"),
            CustomQuestion.prompt.label("prompt"),
            CustomMessage.message.label("message")
                ).join(CustomQuestion)
                 .filter(CustomMessage.user_id == user_id)
                 .filter(CustomQuestion.id == CustomMessage.custom_question_id)
                 .all()
        )
        result = [self.row2dict(obj) for obj in query]
        return result

    def get_client_by_id(self, user_id: int) -> Optional[Client]:
        query = (self.session.query(Client)
                 .join(self.model)
                 .filter(self.model.id == user_id)
                 .filter(Client.id == self.model.client_id)
                 .one_or_none()
                 )
        return query
