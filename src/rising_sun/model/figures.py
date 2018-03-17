# -*- coding: utf-8 -*-
from enum import Enum

from rising_sun.model.base import Id, Instance, List, Model
from rising_sun.model.board import Location
from rising_sun.model.clan import Clan


class FigureType(Enum):
    DAIMYO = '大名'
    BUSHI = '武士'
    SHINTO = '神主'
    MONSTER = '妖怪'


class Figure(Model):
    """
    * A figure can have more than one type, so `types = List`
    * `location == None` means the figure is out of game
    """
    id = Id()
    clan = Instance(Clan, required=True)
    types = List(FigureType, required=True)
    location = Instance(Location)

    @classmethod
    def sample_for_clan(cls, clan):
        return [
            cls(clan=clan, types=[FigureType.DAIMYO]),
            cls(clan=clan, types=[FigureType.SHINTO]),
            cls(clan=clan, types=[FigureType.SHINTO]),
            cls(clan=clan, types=[FigureType.BUSHI]),
            cls(clan=clan, types=[FigureType.BUSHI]),
            cls(clan=clan, types=[FigureType.BUSHI]),
        ]

    @classmethod
    def sample(cls):
        """
        >>> Figure.sample()
        """
        clans = Clan.sample()
        return [f for c in clans for f in cls.sample_for_clan(c)]
