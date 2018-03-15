# -*- coding: utf-8 -*-
from collections import abc  # noqa

from frozendict import FrozenOrderedDict
from pyDatalog import pyDatalog


class Model(pyDatalog.Mixin):

    def __init__(self, **kwargs):
        super(Model, self).__init__()
        self.__dict__.update(kwargs)


class types:  # noqa
    str = str
    int = int
    tuple = tuple
    list = list
    dict = dict
    set = abc.Set

    frozendict = FrozenOrderedDict
    Sequence = abc.Sequence
    Mapping = abc.Mapping


class Column:
    def __init__(self, type_, name=None, default=None, required=False):
        self.type_ = type_
        self.name = name
        self.default = default
        self.required = required

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name, self.default)

    def _preprocess_value(self, value):
        return value

    def __set__(self, instance, value):
        instance.__dict__[self.name] = self._preprocess_value(value)

    def __set_name__(self, owner, name):
        self.owner = owner
        if self.name is None:
            self.name = name


class Instance(Column):
    pass


class List(Column):
    pass


class IndexedList(List):
    def __init__(self, *args, **kwargs):
        self.index = kwargs.pop('index')
        super(IndexedList, self).__init__(*args, **kwargs)

    def _preprocess_value(self, value):
        return types.frozendict((getattr(v, self.index), v) for v in value)

    def __getitem__(self, item):
        raise NotImplementedError
