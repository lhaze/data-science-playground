# -*- coding: utf-8 -*-
from utils.imports import import_all_names
from utils.serialization import load_from_filename
from utils.oss import dirname, path

import_all_names(__file__, __name__)


def sample():
    filename = path(dirname(__file__), 'sample.yaml')
    return load_from_filename(filename)
