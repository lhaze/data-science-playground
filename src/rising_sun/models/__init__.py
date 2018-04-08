# -*- coding: utf-8 -*-
from utils.imports import get_all_names

from .base import get_model, BaseModel, ConfigModel, DbModel


def is_model(cls):
    try:
        return issubclass(cls, BaseModel)
    except TypeError:
        return False


__models__ = get_all_names(__file__, __name__, is_model)
