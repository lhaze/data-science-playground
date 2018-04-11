# -*- coding: utf-8 -*-
import typing as t
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


def get_db_url():
    return 'sqlite://'


@lru_cache(maxsize=1)
def get_db_engine():
    return create_engine(get_db_url(), convert_unicode=True)
    # iff at need of debugging:
    # return create_engine(
    #     get_db_url(),
    #     convert_unicode=True,
    #     echo=True,
    #     # connect_args={'check_same_thread': False}
    # )


@lru_cache(maxsize=1)
def get_session_factory():
    return scoped_session(sessionmaker(bind=get_db_engine()))


def get_session():
    return get_session_factory()()


def create_tables(drop=False):
    session = get_session()
    from rising_sun.models import DbModel
    if drop:
        DbModel.metadata.drop_all()
    DbModel.metadata.create_all()
    DbModel.metadata.session = session
    return DbModel.metadata.tables


def add(instance: 'DbModel', commit: bool = True):
    session = instance.metadata.session
    session.add(instance)
    if commit:
        session.commit()


def get(klass: t.Type['DbModel'], pk: t.Any):
    return klass.query.get(pk)
