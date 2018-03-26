# -*- coding: utf-8 -*-
from pyDatalog import pyDatalog
from ruamel import yaml
from sqlalchemy.ext.declarative import declarative_base

from rising_sun.database import get_db_engine, get_session_factory


class ModelMeta(yaml.YAMLObjectMetaclass, pyDatalog.metaMixin):
    pass


class SimpleModel(yaml.YAMLObject, metaclass=ModelMeta):

    def __init__(self, **kwargs):
        for name, value in kwargs.items():
            validator_name = f'_validate_{name}'
            if hasattr(self, validator_name):
                getattr(self, validator_name)(value)
        self.__dict__.update(kwargs)

    def __getstate__(self):
        """
        Serialization ignores attributes with names starting with `_`.

        >>> from ruamel import yaml
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
