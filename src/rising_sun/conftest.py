# -*- coding: utf-8 -*-
import pytest

from rising_sun.database import create_tables


@pytest.fixture(scope="session", autouse=True)
def init_db():
    """
    Returns session-wide initialised database.
    """
    create_tables()
