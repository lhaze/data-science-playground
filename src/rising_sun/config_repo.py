# -*- coding: utf-8 -*-
import typing as t
from collections import defaultdict
from functools import lru_cache
from weakref import WeakValueDictionary

from utils.os import REPO_PATH
from utils.serialization import load_from_filename

from .base_model import BaseModel


_register = defaultdict(WeakValueDictionary)
_base_class_name = 'BaseModel'
CONFIG_DIR = REPO_PATH / 'rising_sun' / 'config'


def load_config(filename):
    return load_from_filename(CONFIG_DIR / filename)


class Model(BaseModel):

    def __new__(cls, **kwargs):
        """
        Instances of Model are unique with respect to the primary keys, defined with `pk`
        property. The value of the property are values of the attribute described with `__pks__`
        iff it is defined, or objects ID otherwise.
        """
        instance: 'Model' = get(cls.__name__, cls.get_pk(kwargs))
        if instance:
            return instance
        return super().__new__(cls)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        add(self)

    def __setstate__(self, state: t.Mapping):
        super().__setstate__(state)
        add(self)


def add(instance: Model):
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


def remove(instance: Model):
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
