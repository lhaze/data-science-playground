# -*- coding: utf-8 -*-
from collections import defaultdict
from weakref import WeakValueDictionary

from utils.oss import path, REPO_PATH
from utils.serialization import load_from_filename


_register = defaultdict(WeakValueDictionary)
_base_class_name = 'BaseModel'
CONFIG_DIR = REPO_PATH / 'rising_sun' / 'config'


def sample():
    filename = path(CONFIG_DIR, 'war_phase_workout.yaml')
    return load_from_filename(filename)


def add(instance):
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


def remove(instance):
    for klass in instance.__class__.mro():
        _register[klass.__name__].pop(instance.pk)
        if klass == _base_class_name:
            return


def get(klass_name, pk):
    return _register[klass_name].get(pk)


def clear():
    _register.clear()
