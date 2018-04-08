# -*- coding: utf-8 -*-
from collections import defaultdict
from weakref import WeakValueDictionary


_register = defaultdict(WeakValueDictionary)
_base_class_name = 'BaseModel'


def push(instance):
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


def pop(instance):
    for klass in instance.__class__.mro():
        _register[klass.__name__].pop(instance.pk)
        if klass == _base_class_name:
            return


def get(klass_name, pk):
    return _register[klass_name].get(pk)


def clear():
    _register.clear()
