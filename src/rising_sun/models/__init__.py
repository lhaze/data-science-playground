# -*- coding: utf-8 -*-
from utils.imports import get_all_names
from utils.serialization import load_from_filename
from utils.oss import dirname, path

from .base import BaseModel, DbModel, SimpleModel


def is_model(cls):
    try:
        return issubclass(cls, BaseModel)
    except TypeError:
        return False


__models__ = get_all_names(__file__, __name__, is_model)


def get_model(name):
    return __models__.get(name)


def sample():
    filename = path(dirname(__file__), 'sample.yaml')
    return load_from_filename(filename)
