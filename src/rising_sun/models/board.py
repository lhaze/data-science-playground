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


class RewardType(Enum):
    VICTORY_POINTS = 'VPs'
    COINS = 'coins'
    RONINS = 'ronins'


class Location(ConfigModel):

    _pk_keys = ('context', 'name')

    @abc.abstractproperty
    def type(self):
        pass


class RegionSchema(v.Schema):
    name = v.SchemaNode(v.String(), validator=v.Length(1, 10))
    reward = v.SchemaNode(v.Mapping())


class Region(Location):
    yaml_tag = LocationType.REGION.value
    type = LocationType.REGION
    __schema__ = RegionSchema()


class ClanReserveSchema(v.Schema):
    clan = v.SchemaNode(v.Instance('rising_sun.models.clan:Clan'))


class ClanReserve(Location):
    """
    >>> reserves = ClanReserve.sample()
    >>> r = reserves[0]
    >>> r
    ClanReserve(None, Lotus)
    >>> config_repo.get('ClanReserve', (None, 'Koi'))
    ClanReserve(None, Koi)
    """
    yaml_tag = LocationType.RESERVE.value
    type = LocationType.RESERVE
    __schema__ = ClanReserveSchema()

    @property
    def name(self):
        return self.clan.name

    @classmethod
    def sample(cls):
        clans = get_model('Clan').sample()
        return [cls(clan=c) for c in clans]


class Shrine(Location):
    yaml_tag = LocationType.SHRINE.value
    type = LocationType.SHRINE
    kami = None


class Connection(ConfigModel):
    """
    >>> c12 = Connection(a=1, b=2)
    >>> c12
    Connection(None, 1, 2)
    >>> config_repo.get('Connection', (None, 1, 2)) is c12
    True
    >>> c12 == Connection(a=2, b=1)
    True
    """

    yaml_tag = 'connection'
    a = None
    b = None
    is_sea = False
    _pk_keys = ('context', 'a', 'b')

    def __init__(self, **kwargs):
        super(Connection, self).__init__(**kwargs)
        self.a, self.b = min(self.a, self.b), max(self.a, self.b)

    def __eq__(self, other):
        if not isinstance(other, Connection):
            return False
        return (
            (self.a, self.b) == (other.a, other.b) or (self.b, self.a) == (other.a, other.b)
        )


class Map(ConfigModel):

    yaml_tag = 'map'
    regions = ()
    connections = ()

    def validate(self):
        all(r.validate() for r in self.regions)
        all(c.validate() for c in self.connections)
        # validate all regions are connected
        regions_of_connections = chain.from_iterable((c.a, c.b) for c in self.connections)
        assert set(regions_of_connections) == set(r.name for r in self.regions)

    def __repr__(self):
        """
        >>> Map.sample()
        Map(regions=[Nagato,Shikoku,Kansai], connections=[(Kansai,Nagato),(Nagato,Shikoku),(Kansai,Shikoku)])

        """
        return "Map(regions=[{}], connections=[{}])".format(
            ",".join(r.name for r in self.regions),
            ",".join("(%s,%s)" % (c.a, c.b) for c in self.connections),
        )

    @classmethod
    def sample(cls):
        return cls(
            regions=[
                Region(name='Nagato', reward={}),
                Region(name='Shikoku', reward={}),
                Region(name='Kansai', reward={}),
            ],
            connections=[
                Connection(a='Nagato', b='Kansai'),
                Connection(a='Nagato', b='Shikoku',  is_sea=True),
                Connection(a='Shikoku', b='Kansai',  is_sea=True),
            ],
        )


class Board(ConfigModel):

    yaml_tag = 'board'
    map = None
    shrines = ()

    def validate(self):
        self.map.validate()
        all(s.validate() for s in self.shrines)

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
