# -*- coding: utf-8 -*-
import typing as t

# TODO #12. from pyDatalog import pyDatalog, pyParser
from sqlalchemy import Column, String
from sqlalchemy.ext.declarative.base import _add_attribute, _as_declarative

from rising_sun import config_repo
from utils import validation as v
from utils.itertools import recursive_get
from utils.serialization import yaml, CustomLoader


class ModelMeta(yaml.YAMLObjectMetaclass):
    # TODO: #12. inherit pyDatalog.metaMixin
    pass
    #
    # def __init__(cls, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     cls.__terms__ = ()
    #
    #     def class_getattr(instance, name):
    #         """ responds to instance.method by asking datalog engine """
    #         if name not in cls.__terms__:
    #             # the call is a normal getattr
    #             raise AttributeError  # iff attribute name is not a term, attribute is not found
    #         # the call is trying to touch a pyDatalog term
    #         predicate_name = "%s.%s[1]==" % (cls.__name__, name)
    #         terms = (pyParser.Term('_pyD_class', forced_type='constant'), instance, pyParser.Term("X"))  # prefixed
    #         literal = pyParser.Literal.make(predicate_name, terms)  # TODO predicate_name[:-2]
    #         result = literal.lua.ask()
    #         return result[0][-1] if result else None
    #
    #     cls.__getattr__ = class_getattr
    #
    # def __getattr__(self, item):
    #     """
    #     Overrides pyDatalog.metaMixin `__getattr__` and narrows "everything is
    #     a Term" to the list of attributes defined with `__terms__` class attribute.
    #     """
    #     if item in self.__terms__:
    #         return pyParser.Term("%s.%s" % (self.__name__, item))
    #     raise AttributeError


class BaseModel(yaml.YAMLObject, metaclass=ModelMeta):

    yaml_constructor = CustomLoader
    __schema__: v.Schema = None
    __pks__: tuple = None
    context: str = None

    @classmethod
    def get_pk(cls, kwargs):
        if not cls.__pks__:
            return
        return tuple(recursive_get(kwargs, key) for key in cls.__pks__)

    @classmethod
    def _validate(cls, dictionary: t.Mapping):
        if not cls.__schema__:
            return dictionary
        return cls.__schema__.deserialize(dictionary)

    @property
    def pk(self):
        if not self.__pks__:
            return (self.context, id(self))
        return tuple(recursive_get(self, key) for key in self.__pks__)

    def __init__(self, **kwargs):
        validated_kwargs = self._validate(kwargs)
        self.__dict__.update(validated_kwargs)
        super().__init__()

    def __getstate__(self):
        """
        Serialization ignores attributes with names starting with `_`.

        >>> a = BaseModel(foo='bar', _baz='not_serialized')
        >>> yaml.dump(a)
        '!!python/object:rising_sun.base_model.BaseModel {foo: bar}\\n'
        """
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

    def __setstate__(self, state: t.Mapping):
        validated_state = self._validate(state)
        self.__dict__.update(validated_state)

    def __repr__(self):
        return f'{self.__class__.__name__}({", ".join(map(str, self.pk))})'

    def dump(self):
        return yaml.dump(self)


class DbModelMeta(ModelMeta):
    # TODO #12. inherit pyDatalog.sqlMetaMixin

    def __init__(cls, classname, bases, dict_):
        # DeclarativeMeta
        if '_decl_class_registry' not in cls.__dict__:
            _as_declarative(cls, classname, cls.__dict__)
        type.__init__(cls, classname, bases, dict_)

        cls.__schema__ = v.SQLAlchemySchemaNode(cls) if hasattr(cls, '__table__') else None

    def __setattr__(cls, key, value):
        _add_attribute(cls, key, value)


class DbModelBase(BaseModel):
    context = Column(String(20), primary_key=True)


def get_model(name: str) -> BaseModel:
    from .models import __models__
    return __models__.get(name)
