# -*- coding: utf-8 -*-
import abc
from itertools import chain
from enum import Enum

from rising_sun.models.base import SimpleModel


class LocationType(Enum):
    REGION = 'region'
    SHRINE = 'shrine'
    RESERVE = 'reserve'


class RewardType(Enum):
    VICTORY_POINTS = 'VPs'
    COINS = 'coins'
    RONINS = 'ronins'


class Location(SimpleModel):
    name = None

    @abc.abstractproperty
    def type(self):
        pass

    def validate(self):
        assert self.name


class Region(Location):
    yaml_tag = LocationType.REGION.value
    class_symbol = "藩"
    type = LocationType.REGION
    # reward = None

    def validate(self):
        super().validate()
        # assert self.reward in RewardType


class ClanReserve(Location):
    yaml_tag = LocationType.RESERVE.value
    type = LocationType.RESERVE
    clan = None

    def validate(self):
        super().validate()
        self.validate_model_type(self.clan, 'Clan')


class Shrine(Location):
    yaml_tag = LocationType.SHRINE.value
    type = LocationType.SHRINE
    kami = None

    def validate(self):
        super().validate()
        # self.validate_model_type(self.kami, 'Kami')


class Connection(SimpleModel):

    yaml_tag = 'connection'
    descriptor_fields = ('a', 'b')
    a = None
    b = None
    is_sea = False

    @property
    def class_symbol(self):
        return '海' if self.is_sea else '陸'

    def validate(self):
        assert self.a
        assert self.b

    def __eq__(self, other):
        """
        >>> Connection(a=1, b=2) == Connection(a=2, b=1)
        True
        >>> Connection(a=1, b=2, is_sea=True) == Connection(a=1, b=2)
        False
        """
        if not isinstance(other, Connection):
            return False
        return self.is_sea == other.is_sea and (
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
                Region(name='Nagato'),
                Region(name='Shikoku'),
                Region(name='Kansai'),
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
