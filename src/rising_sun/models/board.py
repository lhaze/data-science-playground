# -*- coding: utf-8 -*-
import abc
from itertools import chain
from enum import Enum

from utils import validation as v

from rising_sun import config_repo
from rising_sun.models.base import get_model, ConfigModel


class LocationType(Enum):
    REGION = 'region'
    SHRINE = 'shrine'
    RESERVE = 'reserve'


class Location(ConfigModel):

    _pk_keys = ('context', 'name')

    @abc.abstractproperty
    def type(self):
        pass


class RegionSchema(v.Schema):
    name = v.SchemaNode(v.String(), validator=v.Length(1, 10))
    reward = v.SchemaNode(v.Instance('rising_sun.models.gains:Gain'))


class Region(Location):
    yaml_tag = LocationType.REGION.value
    type = LocationType.REGION
    __schema__ = RegionSchema()


class ClanReserveSchema(v.Schema):
    clan = v.SchemaNode(v.Instance('rising_sun.models.clan:Clan'))


class ClanReserve(Location):
    yaml_tag = LocationType.RESERVE.value
    type = LocationType.RESERVE
    __schema__ = ClanReserveSchema()

    @property
    def name(self):
        return self.clan.name


class ShrineSchema(v.Schema):
    name = v.SchemaNode(v.String(), validator=v.Length(1, 10))
    # kami = v.SchemaNode(v.Instance('rising_sun.models.kami:Kami'), default=None)
    pass


class Shrine(Location):
    yaml_tag = LocationType.SHRINE.value
    type = LocationType.SHRINE
    __schema__ = ShrineSchema()


class ConnectionSchema(v.Schema):
    a = v.SchemaNode(v.Instance(Region))
    b = v.SchemaNode(v.Instance(Region))
    is_sea = v.SchemaNode(v.Bool(), missing=False)

    @staticmethod
    def validator(form, value):
        if value['a'] == value['b']:
            raise v.Invalid(form, f"Source and destination should be different: {value['a']}")


class Connection(ConfigModel):
    """
    >>> r1 = Region(name='1', reward={})
    >>> r2 = Region(name='2', reward={})
    >>> c12 = Connection(a=r1, b=r2)
    >>> c12
    Connection(None, 1, 2)
    >>> config_repo.get('Connection', (None, '1', '2')) is c12
    True
    >>> c12 == Connection(a=r2, b=r1)
    True
    """
    yaml_tag = 'connection'
    _pk_keys = ('context', 'a.name', 'b.name')
    __schema__ = ConnectionSchema()

    def __init__(self, **kwargs):
        super(Connection, self).__init__(**kwargs)
        if self.a.name > self.b.name:
            self.a, self.b = self.b, self.a

    def __eq__(self, other):
        if not isinstance(other, Connection):
            return False
        return (self.a, self.b) == (other.a, other.b)


class MapSchema(v.Schema):
    @v.instantiate()
    class regions(v.SequenceSchema):
        region = v.SchemaNode(v.Instance(Region))

    @v.instantiate()
    class connections(v.SequenceSchema):
        connection = v.SchemaNode(v.Instance(Connection))

    @staticmethod
    def validator(form, value):
        regions_of_connections = set(chain.from_iterable((c.a, c.b) for c in value['connections']))
        all_regions = set(value['regions'])
        if regions_of_connections != all_regions:
            raise v.Invalid(form, (
                f'Regions defined by connections ({regions_of_connections}) '
                f'do not match all regions provided ({all_regions})'
            ))


class Map(ConfigModel):
    yaml_tag = 'map'
    __schema__ = MapSchema()

    def __repr__(self):
        """
        >>> Map.sample()
        Map(regions=[Nagato,Shikoku,Kansai], connections=[(Kansai,Nagato),(Nagato,Shikoku),(Kansai,Shikoku)])

        """
        return "Map(regions=[{}], connections=[{}])".format(
            ",".join(r.name for r in self.regions),
            ",".join("(%s,%s)" % (c.a.name, c.b.name) for c in self.connections),
        )

    @classmethod
    def sample(cls):
        regions = [
            Region(name='Nagato', reward={}),
            Region(name='Shikoku', reward={}),
            Region(name='Kansai', reward={}),
        ]
        return cls(
            regions=regions,
            connections=[
                Connection(a=regions[0], b=regions[2]),
                Connection(a=regions[0], b=regions[1],  is_sea=True),
                Connection(a=regions[1], b=regions[2],  is_sea=True),
            ],
        )


class BoardSchema(v.Schema):
    map = v.SchemaNode(v.Instance(Map))

    @v.instantiate(missing=())
    class shrines(v.SequenceSchema):
        shrine = v.SchemaNode(v.Instance(Shrine))


class Board(ConfigModel):
    yaml_tag = 'board'
    __schema__ = BoardSchema()

    @classmethod
    def sample(cls):
        return cls(
            map=Map.sample(),
            shrines=[
                Shrine(name='Shrine 1'),
                Shrine(name='Shrine 2'),
                Shrine(name='Shrine 3'),
                Shrine(name='Shrine 4'),
            ]
        )
