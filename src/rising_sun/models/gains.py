# -*- coding: utf-8 -*-
from enum import Enum

from rising_sun.base_model import BaseModel
from utils import validation as v


class GainType(Enum):
    VICTORY_POINTS = 'vps'
    COINS = 'coins'
    RONINS = 'ronins'
    HONOR = 'honor'


GainSchema = type(
    'Reward',
    (v.Schema,),
    {
        gain_type.value: v.SchemaNode(v.Int(), validator=v.Range(-10, 10), missing=v.drop, default=0)
        for gain_type in GainType
    }
)


class Gain(BaseModel):
    __pks__ = tuple(gain_type.value for gain_type in GainType)
    __schema__ = GainSchema(v.Mapping(unknown='raise'))
