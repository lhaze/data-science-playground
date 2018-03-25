# -*- coding: utf-8 -*-
from pyDatalog import pyDatalog
from sqlalchemy.ext.declarative import declarative_base

from rising_sun.database import get_db_engine, get_session_factory


class Base(pyDatalog.Mixin):

    query = get_session_factory().query_property()

    def __init__(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)

    def store(self):
        session = self.metadata.session
        session.add(self)
        session.commit()


Model = declarative_base(cls=Base, metaclass=pyDatalog.sqlMetaMixin)
Model.metadata.bind = get_db_engine()
