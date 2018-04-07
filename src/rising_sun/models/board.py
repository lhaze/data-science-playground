# -*- coding: utf-8 -*-
import abc
from itertools import chain
from enum import Enum

from utils.serialization import c

from rising_sun.models.base import get_model, SimpleModel


class LocationType(Enum):
    REGION = 'region'
    SHRINE = 'shrine'
    RESERVE = 'reserve'


class RewardType(Enum):
    VICTORY_POINTS = 'VPs'
    COINS = 'coins'
    RONINS = 'ronins'


class Location(SimpleModel):

    @abc.abstractproperty
    def type(self):
        pass


class RegionSchema(c.Schema):
    name = c.SchemaNode(c.String(), validator=c.Length(1, 10))
    reward = c.SchemaNode(c.Mapping())


class Region(Location):
    yaml_tag = LocationType.REGION.value
    class_symbol = "藩"
    type = LocationType.REGION
    __schema__ = RegionSchema()

    @property
    def pk(self):
        return self.name


class ClanReserveSchema(c.Schema):
    clan = c.SchemaNode(c.Instance('rising_sun.models.clan:Clan'))


class ClanReserve(Location):
    """
    >>> reserves = ClanReserve.sample()
    >>> r = reserves[0]
    >>> r
    ClanReserve(Lotus)
    >>> ClanReserve.get('Koi')
    ClanReserve(Koi)
    """
    yaml_tag = LocationType.RESERVE.value
    type = LocationType.RESERVE
    __schema__ = ClanReserveSchema()

    @property
    def pk(self):
        return self.clan.name

    def __repr__(self):
        return f"ClanReserve({self.clan.name})"

    @classmethod
    def sample(cls):
        clans = get_model('Clan').sample()
        return [cls(clan=c) for c in clans]


class Shrine(Location):
    yaml_tag = LocationType.SHRINE.value
    type = LocationType.SHRINE
    kami = None
    number = None

    @property
    def pk(self):
        return self.number


class Connection(SimpleModel):
    """
    >>> c12 = Connection(a=1, b=2)
    >>> c21 = Connection(a=2, b=1)
    >>> c12s = Connection(a=1, b=2, is_sea=True)
    >>> c12
    陸(a=1, b=2)
    >>> c12s
    海(a=1, b=2)
    >>> c12 == c21
    True
    >>> c12 == c12s
    True
    >>> Connection.get((1, 2)) is c12
    True
    """

    yaml_tag = 'connection'
    descriptor_fields = ('a', 'b')
    a = None
    b = None
    is_sea = False

    @property
    def pk(self):
        return (self.a, self.b)

    @property
    def class_symbol(self):
        return '海' if self.is_sea else '陸'

    def validate(self):
        assert self.a
        assert self.b

    def __eq__(self, other):
        if not isinstance(other, Connection):
            return False
        return (
            (self.a, self.b) == (other.a, other.b) or (self.b, self.a) == (other.a, other.b)
        )


class Map(SimpleModel):

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
        Map(regions=[Nagato,Shikoku,Kansai], connections=[(Nagato,Kansai),(Nagato,Shikoku),(Shikoku,Kansai)])

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


class Board(SimpleModel):

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
