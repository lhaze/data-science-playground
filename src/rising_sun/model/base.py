# -*- coding: utf-8 -*-
from pyDatalog import pyDatalog
from sqlalchemy.ext.declarative import declared_attr, declarative_base

from utils.text import camelcase_to_snake_case
from rising_sun.db_session import get_db_session


class Base(pyDatalog.Mixin):

    @declared_attr
    def __tablename__(cls):
        return camelcase_to_snake_case(cls.__name__)


Model = declarative_base(cls=Base, metaclass=pyDatalog.sqlMetaMixin)
Model.session = get_db_session()
