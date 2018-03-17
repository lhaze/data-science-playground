# -*- coding: utf-8 -*-
import abc
from collections import abc as collections_abc
from itertools import count
from operator import attrgetter

from frozendict import FrozenOrderedDict
from pyDatalog import pyDatalog


class Model(pyDatalog.Mixin):

    @classmethod
    def __init_subclass__(cls):
        cls._fields = types.FrozenOrderedDict(
            (name, field) for name, field in cls.__dict__.items()
            if isinstance(field, Field)
        )

    def __init__(self, **kwargs):
        super(Model, self).__init__()
        for name, field in self._fields.items():
            if field.required and name not in kwargs:
                raise ValueError('Field {} value for {} not provided.'.format(name, self))
            value = kwargs.pop(name, field.default)
            setattr(self, name, value)
            field.init(self)


class types:  # noqa
    str = str
    int = int
    tuple = tuple
    list = list
    dict = dict
    set = collections_abc.Set
    Sequence = collections_abc.Sequence
    Mapping = collections_abc.Mapping
    FrozenOrderedDict = FrozenOrderedDict


class Field(metaclass=abc.ABCMeta):
    def __init__(self, type_, name=None, default=None, required=False):
        self.type_ = type_
        self.name = name
        self.default = default
        self.required = required

    def init(self, instance):
        """Initialize instance of the owner with this field."""

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name, self.default)

    def _preprocess_value(self, value):
        return value

    def __set__(self, instance, value):
        self._validate_value(value)
        instance.__dict__[self.name] = self._preprocess_value(value)

    def __set_name__(self, owner, name):
        self.owner = owner
        if self.name is None:
            self.name = name

    @abc.abstractmethod
    def _validate_value(self, value):
        raise NotImplementedError


class Instance(Field):
    """
    A field that holds an instance of a `type_`.
    """
    def _validate_value(self, value):
        if not isinstance(value, self.type_):
            raise ValueError()


class Id(Instance):

    def __init__(self, name=None):
        super(Id, self).__init__(int, name=name, required=True)

    def __set_name__(self, owner, name):
        super(Id, self).__set_name__(owner, name)
        owner._id_counter = count()

    def init(self, instance):
        self.__set__(instance, self.owner._id_counter())


class List(Field):
    """
    A field that holds an iterable of instances of a `type_`.
    """
    def _validate_value(self, value):
        if not all(isinstance(v, self.type_) for v in value):
            raise ValueError()


class IndexedList(List):
    """
    This field gets iterables of `type_` as values but then turns to a Mapping based on index
    field(s) of the objects examined.
    """
    def __init__(self, *args, **kwargs):
        index = kwargs.pop('index')
        if isinstance(index, str):
            index = (index,)
        self.index = index
        super(IndexedList, self).__init__(*args, **kwargs)

    def _preprocess_value(self, value):
        return types.FrozenOrderedDict((attrgetter(*self.index)(v), v) for v in value)

    def __getitem__(self, item):
        raise NotImplementedError
