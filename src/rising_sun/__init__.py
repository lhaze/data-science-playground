# -*- coding: utf-8 -*-
from utils.oss import path, REPO_PATH
from utils.serialization import load_from_filename

from rising_sun import db_repo, simple_repo
from rising_sun.models import *


CONFIG_DIR = REPO_PATH / 'rising_sun' / 'config'


def sample():
    filename = path(CONFIG_DIR, 'war_phase_workout.yaml')
    return load_from_filename(filename)
