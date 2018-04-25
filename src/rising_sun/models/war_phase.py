# -*- coding: utf-8 -*-
from sqlalchemy import Column, ForeignKey, Integer, Unicode
from sqlalchemy.orm import relationship, validates

from rising_sun.models.base import config_repo, ConfigModel, DbModel
from utils import validation as v
from utils.functools import reify


class AdvantageSchema(v.Schema):
    name = v.SchemaNode(v.String(), validator=v.Length(max=20))
    procedure = v.SchemaNode(v.String(), validator=v.Length(max=20))


class Advantage(ConfigModel):
    yaml_tag = 'advantage'
    _pk_keys = ('context', 'name')
    __schema__ = AdvantageSchema()


class AdvantageBid(DbModel):
    __tablename__ = 'advantage_bid'
    _pk_keys = ('context', 'name')

    advantage_name = Column(Unicode(20), primary_key=True)
    clan_name = Column(Unicode(20), ForeignKey('clan.name'), primary_key=True)
    clan = relationship("Clan")
    coins = Column(Integer())

    @reify
    def advantage(self):
        return config_repo.get("Advantage", (self.context, self.advantage_name))
