# -*- coding: utf-8 -*-
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def get_db_url():
    # create database in memory
    return 'sqlite://'


@lru_cache(maxsize=16)
def get_db_engine(db_url_factory=get_db_url):
    return create_engine(db_url_factory(), echo=False)


@lru_cache(maxsize=16)
def get_db_session(db_engine_factory=get_db_engine):
    # open a session on a database
    session_factory = sessionmaker(bind=db_engine_factory())
    return session_factory()
