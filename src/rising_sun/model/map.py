# -*- coding: utf-8 -*-
from collections import namedtuple

from rising_sun.model.base import types, Instance, IndexedList, Model


class Region(Model):
    symbol = Instance(str, required=True)
    name = Instance(str)
    reward = Instance(types.Mapping, default=types.frozenordereddict())

    def __init__(self, **kwargs):
        super(Region, self).__init__(**kwargs)

    def __repr__(self):
        """
        >>> Region(symbol='K', name='Kyushu')
        藩(K)
        """
        return "藩({})".format(self.symbol)


class Connection(namedtuple('Connection', 'a, b')):

    def __new__(cls, *args, is_sea=False):
        self = super(Connection, cls).__new__(cls, *args)
        self.is_sea_route = is_sea
        return self

    def __repr__(self):
        """
        >>> Connection(1, 2, is_sea=True)
        海(1,2)
        >>> Connection(2, 1)
        陸(2,1)
        """
        return "{}({},{})".format('海' if self.is_sea_route else '陸', self.a, self.b)

    def __eq__(self, other):
        """
        >>> Connection(1, 2) == Connection(2, 1)
        True
        >>> Connection(1, 2, is_sea=True) == Connection(1, 2)
        True
        """
        if not isinstance(other, Connection):
            return False
        return (self.a, self.b) == (other.a, other.b) or (self.b, self.a) == (other.a, other.b)


class Map(Model):
    regions = IndexedList(Region, index='symbol', default=())
    connections = IndexedList(Connection, index=('a', 'b'), default=())

    def __getitem__(self, item):
        return self.regions[item]

    def __repr__(self):
        """
        >>> Map.sample()
        Map(regions=[N,S,K], connections=[(N,K),(N,S),(S,K)])

        """
        return "Map(regions=[{}], connections=[{}])".format(
            ",".join(r.symbol for r in self.regions.values()),
            ",".join("(%s,%s)" % (c.a, c.b) for c in self.connections.values()),
        )

    @classmethod
    def sample(cls):
        return cls(
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
