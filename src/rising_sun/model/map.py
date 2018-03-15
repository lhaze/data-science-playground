# -*- coding: utf-8 -*-
from collections import namedtuple

from rising_sun.model.base import Instance, IndexedList, Model


class Region(Model):
    symbol = Instance(str, required=True)
    name = Instance(str)


class Connection(namedtuple('Connection', 'a, b')):

    def __new__(cls, *args, is_sea=False):
        """
        >>> Connection(1, 2, is_sea=True)
        """
        self = super(Connection, cls).__new__(cls, *args)
        self.is_sea_route = is_sea
        return self

    def __eq__(self, other):
        """
        >>> Connection(1, 2) == Connection(2, 1)
        True
        >>> Connection(1, 2, is_sea=True) == Connection(1, 2)
        True
        """
        if not isinstance(other, Connection):
            return False
        return (self.a, self.b) == other or (self.b, self.a) == other


class Map(Model):
    regions = IndexedList(Region, index='symbol', default=())
    connections = IndexedList(Connection, index=('a', 'b'), default=())

    def __getitem__(self, item):
        return self.regions[item]


def sample():
    return Map(
        regions=(
            Region(symbol='N', name='Nagato'),
            Region(symbol='S', name='Shikoku'),
            Region(symbol='K', name='Kansai'),
        ),
        connections=(
            Connection('N', 'K'),
            Connection('N', 'S',  is_sea=True),
            Connection('S', 'K',  is_sea=True),
        ),
    )
