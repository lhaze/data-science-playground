# -*- coding: utf-8 -*-
from pyDatalog import pyDatalog, pyParser
from ruamel import yaml
from sqlalchemy.ext.declarative import declarative_base

from rising_sun.database import get_db_engine, get_session_factory


VALIDATOR_ATTR = '_model_validates'


class ModelMeta(yaml.YAMLObjectMetaclass, pyDatalog.metaMixin):
    __terms__ = ()

    def __getattr__(self, item):
        """
        Overrides pyDatalog.metaMixin `__getattr__` and narrows "everything is
        a Term" to the list of attributes defined with `__terms__` class attribute.
        """
        if item in self._predicates:
            return pyParser.Term("%s.%s" % (self.__name__, item))
        raise AttributeError


class SimpleModel(yaml.YAMLObject, metaclass=ModelMeta):

    def __init_subclass__(cls, **kwargs):
        """
        Gathers all model validators in `_validators` dict per (sub)class.
        """
        super().__init_subclass__(**kwargs)
        cls._validators = {}
        for name in dir(cls):
            function = getattr(cls, name)
            validates = getattr(function, VALIDATOR_ATTR, None)
            if validates:
                cls._validators[name] = (function,) + validates

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __getstate__(self):
        """
        Serialization ignores attributes with names starting with `_`.

        >>> a = SimpleModel(foo='bar', _baz='not_serialized')
        >>> yaml.dump(a)
        '!!python/object:base.SimpleModel {foo: bar}\\n'
        """
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

    def __repr__(self):
        return '{0}({1})'.format(
            self.__class__.__name__,
            ", ".join(
                "{}={}".format(k, v)
                for k, v in sorted(self.__dict__.items())
                if not k.startswith('_')
            )
        )


def model_validator(*names):
    def marker(f):
        setattr(f, VALIDATOR_ATTR, names)
        return f
    return marker


def save(model, commit=True):
    session = model.metadata.session
    session.add(model)
    if commit:
        session.commit()


class DbModelMeta(pyDatalog.sqlMetaMixin, ModelMeta):
    pass


DbModel = declarative_base(cls=SimpleModel, metaclass=DbModelMeta)
DbModel.metadata.bind = get_db_engine()
DbModel.query = get_session_factory().query_property()
DbModel.save = save


class Region(SimpleModel):
    """
    >>> region = Region(symbol='K', name='Kansai', reward={})
    >>> string = yaml.dump(region)
    >>> string
    '!<Region>\\nname: Kansai\\nreward: {}\\nsymbol: K\\n'
    >>> restored_region = yaml.load(string, Loader=yaml.Loader)
    >>> restored_region
    Region(name=Kansai, reward={}, symbol=K)
    """
    yaml_tag = 'Region'

    @classmethod
    def sample(cls):
        """
        >>> sample = Region.sample()
        >>> yaml.dump(sample)  # doctest: +ELLIPSIS
        '- !<Region>\\n  name: Nagato\\n  reward: {}\\n  symbol: N\\n- ... symbol: K\\n'
        """
        return [
            Region(symbol='N', name='Nagato', reward={}),
            Region(symbol='S', name='Shikoku', reward={}),
            Region(symbol='K', name='Kansai', reward={}),
        ]
