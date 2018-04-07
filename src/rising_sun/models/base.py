# -*- coding: utf-8 -*-
import abc
import typing as t

from pyDatalog import pyDatalog, pyParser
from sqlalchemy.ext.declarative import declarative_base

from rising_sun.database import get_db_engine, get_session_factory
from utils.serialization import c, yaml, ExtLoader


class ModelMeta(yaml.YAMLObjectMetaclass, pyDatalog.metaMixin):

    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls.__terms__ = ()

        def class_getattr(instance, name):
            """ responds to instance.method by asking datalog engine """
            if name not in cls.__terms__:
                # the call is a normal getattr
                raise AttributeError
            # the call is trying to touch a pyDatalog term
            predicate_name = "%s.%s[1]==" % (cls.__name__, name)
            terms = (pyParser.Term('_pyD_class', forced_type='constant'), instance, pyParser.Term("X"))  # prefixed
            literal = pyParser.Literal.make(predicate_name, terms)  # TODO predicate_name[:-2]
            result = literal.lua.ask()
            return result[0][-1] if result else None

        cls.__getattr__ = class_getattr

    def __getattr__(self, item):
        """
        Overrides pyDatalog.metaMixin `__getattr__` and narrows "everything is
        a Term" to the list of attributes defined with `__terms__` class attribute.
        """
        if item in self.__terms__:
            return pyParser.Term("%s.%s" % (self.__name__, item))
        raise AttributeError


class BaseModel(yaml.YAMLObject, metaclass=ModelMeta):

    yaml_constructor = ExtLoader
    __schema__ = None  # type: c.Schema

    @property
    def class_symbol(self):
        return self.__class__.__name__

    @property
    def descriptor_fields(self):
        return sorted(name for name in self.__dict__ if not name.startswith('_'))

    @abc.abstractclassmethod
    def get(cls, pk):
        """Returns the instance marked with given primary key"""

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        super().__init__()

    def __getstate__(self):
        """
        Serialization ignores attributes with names starting with `_`.

        >>> a = BaseModel(foo='bar', _baz='not_serialized')
        >>> yaml.dump(a)
        '!!python/object:rising_sun.models.base.BaseModel {foo: bar}\\n'
        """
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

    def __repr__(self):
        return '{0}({1})'.format(
            self.class_symbol,
            ", ".join(
                "{}={}".format(name, getattr(self, name))
                for name in self.descriptor_fields
            )
        )

    def dump(self):
        return yaml.dump(self)

    def validate(self):
        if not self.__schema__:
            return
        serialized = self.__schema__.serialize()
        return self.__schema__.deserialize(serialized)


class SimpleModel(BaseModel):

    _pk_register = {}

    @property
    def pk(self):
        return id(self)

    @classmethod
    def get(cls, pk):
        return cls._pk_register.get(pk)

    def __init__(self, **kwargs):
        if self.__schema__:
            kwargs = self.__schema__.deserialize(kwargs)

        super().__init__(**kwargs)

        if self.pk in self._pk_register:
            assert self == self._pk_register[self.pk], (
                f"Class {self.__class__.__name__} tried to overshadow object "
                f"{self._pk_register[self.pk]} with {self} in the class register."
            )
        else:
            self._pk_register[self.pk] = self


class DbModelMeta(ModelMeta, pyDatalog.sqlMetaMixin):
    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls.__schema__ = c.SQLAlchemySchemaNode(cls) if hasattr(cls, '__table__') else None


class DbModel(declarative_base(
    bind=get_db_engine(),
    cls=BaseModel,
    metaclass=DbModelMeta,
    name='DbModel'
)):
    __abstract__ = True
    query = get_session_factory().query_property()

    def __init__(self, **kwargs):
        if self.__schema__:
            self.__schema__.deserialize(kwargs)
        super().__init__(**kwargs)

    def save(self, commit: bool = True):
        session = self.metadata.session
        session.add(self)
        if commit:
            session.commit()

    def get(self, pk: t.Any):
        return self.query.get(pk)


def get_model(name: str) -> BaseModel:
    from . import __models__
    return __models__.get(name)
