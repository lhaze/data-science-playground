# -*- coding: utf-8 -*-
from enum import Enum

from sqlalchemy import Column, Unicode
from sqlalchemy.orm.mapper import validates

from rising_sun.models.base import config_repo, ConfigModel, DbModel
from utils import validation as v
from utils.functools import reify


class ClanColors(Enum):
    red = 'red'
    orange = 'orange'
    blue = 'blue'


class ClanTypeSchema(v.Schema):
    name = v.SchemaNode(v.String(), validator=v.Length(max=20))
    color = v.SchemaNode(v.String(), validator=v.OneOf(c.value for c in ClanColors))
    starting_honor = v.SchemaNode(v.Integer(), validator=v.Range(1, 10))
    starting_coins = v.SchemaNode(v.Integer(), validator=v.Range(1, 10))
    region = v.SchemaNode(v.Instance('rising_sun.models.board:Region'))


class ClanType(ConfigModel):
    yaml_tag = 'clan_type'
    __pks__ = ('context', 'name')
    __schema__ = ClanTypeSchema()


class Clan(DbModel):
    __tablename__ = 'clan'
    __pks__ = ('context', 'name')

    name = Column(Unicode(20), primary_key=True)
    assets = None

    @reify
    def type(self):
        return config_repo.get("ClanType", (self.context, self.name))

    @reify
    def reserve(self):
        return config_repo.get("ClanReserve", (self.context, self.name))

    @validates("name")
    def validate_name(self, key, name):
        assert name in config_repo.filter("ClanType", lambda pk: pk[0] == self.context)
        return name
