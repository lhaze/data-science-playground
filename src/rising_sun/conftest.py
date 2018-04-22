# -*- coding: utf-8 -*-
import pytest

from rising_sun import config_repo, db_repo


@pytest.fixture(scope="session", autouse=True)
def init_db():
    """
    Initializes database session-wide.
    """
    db_repo.create_tables()


@pytest.fixture(scope="session", autouse=True)
def load_config_models():
    """
    Initializes config session-wide.
    """
    config_repo.clear()
    config_repo.load_config('battle_workout.yaml')
