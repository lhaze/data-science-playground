# -*- coding: utf-8 -*-
from sqlalchemy import Column, Unicode
from sqlalchemy.orm.mapper import validates

from rising_sun.models.base import config_repo, ConfigModel, DbModel
from utils import validation as v
from utils.functools import reify


class ClanTypeSchema(v.Schema):
    name = 'Koi'
    color = 'red'
    starting_honor = 1
    starting_coins: 5
    region = v.SchemaNode(v.Instance('rising_sun.models.board:Region'))


class ClanType(ConfigModel):
    yaml_tag = 'clantype'
    _pk_keys = ('context', 'name')
    __schema__ = ClanTypeSchema()


class Clan(DbModel):
    __tablename__ = 'clan'
    _pk_keys = ('context', 'name')

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
