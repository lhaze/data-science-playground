# -*- coding: utf-8 -*-
import pytest


@pytest.fixture(scope='session', autouse=True)
def db_create_tables():
    from rising_sun.db_session import get_db_engine
    from rising_sun.model.base import Model
    Model.metadata.create_all(get_db_engine())
