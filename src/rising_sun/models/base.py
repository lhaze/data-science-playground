# -*- coding: utf-8 -*-
import abc
import typing as t

from pyDatalog import pyDatalog, pyParser
from sqlalchemy.ext.declarative import declarative_base

from rising_sun import config_repo, db_repo
from utils.serialization import c, yaml, ExtLoader


class ModelMeta(yaml.YAMLObjectMetaclass, pyDatalog.metaMixin):

    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls.__terms__ = ()

        def class_getattr(instance, name):
            """ responds to instance.method by asking datalog engine """
            if name not in cls.__terms__:
                # the call is a normal getattr
                raise AttributeError  # iff attribute name is not a term, attribute is not found
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
    _pk_key = None

    @classmethod
    def get_pk(cls, kwargs):
        return kwargs.get(cls._pk_key)

    @property
    def pk(self):
        return getattr(self, self._pk_key) if self._pk_key else id(self)

    def __init__(self, **kwargs):
        if self.__schema__:
            kwargs = self.__schema__.deserialize(kwargs)
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
        return f'{self.__class__.__name__}({self.pk})'

    def dump(self):
        return yaml.dump(self)

    def validate(self):
        if not self.__schema__:
            return
        serialized = self.__schema__.serialize()
        return self.__schema__.deserialize(serialized)


class ConfigModel(BaseModel):

    def __new__(cls, **kwargs):
        """
        Instances of ConfigModel are unique with respect to the primary key, defined with `pk`
        property. The value of the property are values of the attribute described with `_pk_key`
        iff it is defined, or objects ID otherwise.
        """
        instance = config_repo.get(cls.__name__, cls.get_pk(kwargs))
        return instance if instance else super().__new__(cls)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        config_repo.add(self)

    def __setstate__(self, d):
        if self.__schema__:
            d = self.__schema__.deserialize(d)
        self.__dict__.update(d)
        config_repo.add(self)


class DbModelMeta(ModelMeta, pyDatalog.sqlMetaMixin):
    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls.__schema__ = c.SQLAlchemySchemaNode(cls) if hasattr(cls, '__table__') else None


class DbModel(declarative_base(
    bind=db_repo.get_db_engine(),
    cls=BaseModel,
    metaclass=DbModelMeta,
    name='DbModel'
)):
    __abstract__ = True
    query = db_repo.get_session_factory().query_property()

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
