# -*- coding: utf-8 -*-
from sqlalchemy import Column, ForeignKey, Integer, Unicode
from sqlalchemy.orm import relationship

from rising_sun import config_repo, db_repo
from utils import validation as v
from utils.functools import reify


class AdvantageSchema(v.Schema):
    name = v.SchemaNode(v.String(), validator=v.Length(max=20))
    procedure = v.SchemaNode(v.String(), validator=v.Length(max=20))


class Advantage(config_repo.Model):
    yaml_tag = 'advantage'
    __pks__ = ('context', 'name')
    __schema__ = AdvantageSchema()


class AdvantageBid(db_repo.Model):
    __tablename__ = 'advantage_bid'
    __pks__ = ('context', 'name')

    advantage_name = Column(Unicode(20), primary_key=True)
    clan_name = Column(Unicode(20), ForeignKey('clan.name'), primary_key=True)
    clan = relationship("Clan")
    coins = Column(Integer())

    @reify
    def advantage(self):
        return config_repo.get("Advantage", (self.context, self.advantage_name))
