# -*- coding: utf-8 -*-
from collections import abc  # noqa
from operator import attrgetter

from frozendict import FrozenOrderedDict
from pyDatalog import pyDatalog


class Model(pyDatalog.Mixin):

    def __init__(self, **kwargs):
        super(Model, self).__init__()
        for name, field in self.__class__.__dict__.items():
            if isinstance(field, Column):
                if field.required and name not in kwargs:
                    raise ValueError('Field {} value for {} not provided.'.format(name, self))
                value = kwargs.pop(name, field.default)
                setattr(self, name, value)


class types:  # noqa
    str = str
    int = int
    tuple = tuple
    list = list
    dict = dict
    set = abc.Set

    frozenordereddict = FrozenOrderedDict
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
        index = kwargs.pop('index')
        if isinstance(index, str):
            index = (index,)
        self.index = index
        super(IndexedList, self).__init__(*args, **kwargs)

    def _preprocess_value(self, value):
        return types.frozenordereddict((attrgetter(*self.index)(v), v) for v in value)

    def __getitem__(self, item):
        raise NotImplementedError
