from typing import Optional, Type
from ..schema import Base
from sqlalchemy.orm import Session
from sqlalchemy import update, delete
import traceback


def sql_check(method):
    def wrapper(ref, *args, **kwargs):
        try:
            return method(ref, *args, **kwargs)
        except Exception:
            print(traceback.format_exc())
            ref.session.rollback()
            print("Rolling back session...")
    return wrapper


class SQLService:
    model: Type[Base]

    def __init__(self, session: Session):
        self.session: Session = session

    @sql_check
    def create(self, object: dict, commit: bool = True, **kwargs):
        """
        Create a row by passing a dict.
        :param object:
        :param commit:
        :return:
        """
        object = self.model(**object)
        self.insert(object, commit=True)
        self.session.refresh(object)
        return object.id

    def row2dict(self, obj):
        try:
            d = obj.__dict__
            d.pop('_sa_instance_state')
        except AttributeError:
            d = obj._mapping
        return d

    @sql_check
    def insert(self, object, commit: bool = True):
        """
        :param object:
        :param commit:
        :return:
        """
        self.session.add(object)
        if commit:
            self.session.commit()
        return True

    @sql_check
    def insert_table(self, table, obj, commit: bool = True):
        ins = table.insert().values(**obj)
        self.session.execute(ins)
        if commit:
            self.session.commit()
        return True

    @sql_check
    def delete(self, ids: list[int], commit: bool = True):
        self.session.query(self.model).filter(self.model.id.in_(ids)).delete()
        if commit:
            self.session.commit()
        return True

    @sql_check
    def update(self, object: dict, commit: bool = True):

        self.session.execute(
            update(self.model),
                [object]
        )

        if commit:
            self.session.commit()
        return True

    @sql_check
    def get_by_id(self, id: int):
        """

        :param id:
        :return:
        """
        return self.session.query(self.model).filter(self.model.id == id).one_or_none()

    def get_by_id_dict(self, id: int):
        obj = self.get_by_id(id)
        return self.row2dict(obj)

    @sql_check
    def commit(self):
        self.session.commit()
        return