# -*- coding: utf-8 -*-
import typing as t
from collections import defaultdict
from functools import lru_cache
from weakref import WeakValueDictionary

from utils.oss import REPO_PATH
from utils.serialization import load_from_filename


_register = defaultdict(WeakValueDictionary)
_base_class_name = 'BaseModel'
CONFIG_DIR = REPO_PATH / 'rising_sun' / 'config'


def load_config(filename):
    return load_from_filename(CONFIG_DIR / filename)


def add(instance: 'ConfigModel'):
    for klass in instance.__class__.mro():
        if klass.__name__ == _base_class_name:
            return
        assert (
            instance.pk not in _register[klass.__name__] or
            _register[klass.__name__][instance.pk] is instance
        ), (
            f"Class {instance.__class__.__name__} tried to overshadow object "
            f"{_register[klass.__name__][instance.pk]} with {instance} in the class register."
        )
        _register[klass.__name__][instance.pk] = instance


def remove(instance: 'ConfigModel'):
    for klass in instance.__class__.mro():
        _register[klass.__name__].pop(instance.pk)
        if klass == _base_class_name:
            return


def get(klass_name: str, pk: t.Tuple):
    return _register[klass_name].get(pk) if pk else None


@lru_cache(maxsize=64)
def filter(klass_name: str, condition: t.Callable[[t.Tuple], bool]):
    return [model for pk, model in _register[klass_name].items() if condition(pk)]


def clear():
    _register.clear()
