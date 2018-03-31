# -*- coding: utf-8 -*-
import abc

from pyDatalog import pyDatalog, pyParser
from sqlalchemy.ext.declarative import declarative_base

from rising_sun.database import get_db_engine, get_session_factory
from utils.serialization import yaml, ExtLoader
from utils.traits import Entity


class ModelMeta(yaml.YAMLObjectMetaclass, pyDatalog.metaMixin):
    __terms__ = ()

    def __getattr__(self, item):
        """
        Overrides pyDatalog.metaMixin `__getattr__` and narrows "everything is
        a Term" to the list of attributes defined with `__terms__` class attribute.
        """
        if item in self.__terms__:
            return pyParser.Term("%s.%s" % (self.__name__, item))
        raise AttributeError


class BaseModel(Entity, yaml.YAMLObject, metaclass=ModelMeta):

    yaml_constructor = ExtLoader

    @property
    def class_symbol(self):
        return self.__class__.__name__

    @property
    def descriptor_fields(self):
        return sorted(name for name in self.__dict__ if not name.startswith('_'))

    @property
    def pk(self):
        """
        Describes primary key of the instance.
        Supply `name` field in the concrete subclasses or reimplement it.
        """
        return self.name

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


class SimpleModel(BaseModel):

    _pk_register = {}

    @classmethod
    def get(cls, pk):
        return cls._pk_register.get(pk)

    def __init__(self, **kwargs):
        super(SimpleModel, self).__init__(**kwargs)
        assert self.pk not in self._pk_register, (
            f"Class {self.__class__.__name__} tried to overshadow object "
            f"{self._pk_register[self.pk]} with {self} in the class register."
        )
        self._pk_register[self.pk] = self


class DbModelMeta(ModelMeta, pyDatalog.sqlMetaMixin):
    pass


DbModel = declarative_base(
    bind=get_db_engine(),
    cls=BaseModel,
    metaclass=DbModelMeta,
    name='DbModel'
)


def save(model: DbModel, commit: bool = True):
    session = model.metadata.session
    session.add(model)
    if commit:
        session.commit()


DbModel._query = get_session_factory().query_property()
DbModel.save = save
