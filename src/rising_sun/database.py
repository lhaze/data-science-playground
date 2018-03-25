# -*- coding: utf-8 -*-
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
    from rising_sun.models import Model
    if drop:
        Model.metadata.drop_all()
    Model.metadata.create_all()
    Model.metadata.session = session
    return Model.metadata.tables


def example():
    from rising_sun.models import Region
    r = Region(symbol='K', name='Kansai')
    r.store()
    return Region.query.all()
