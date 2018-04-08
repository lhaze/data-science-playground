# -*- coding: utf-8 -*-
import pytest

from rising_sun import db_repo


@pytest.fixture(scope="session", autouse=True)
def init_db():
    """
    Returns session-wide initialised database.
    """
    db_repo.create_tables()
