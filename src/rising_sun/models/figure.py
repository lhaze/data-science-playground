# -*- coding: utf-8 -*-
from enum import Enum

from sqlalchemy import Column, ForeignKey, Integer, Unicode
from sqlalchemy.orm import relationship

from rising_sun import config_repo, db_repo
from utils import validation as v
from utils.functools import reify


class FigureCategory(Enum):
    DAIMYO = 'DAIMYO'  # 大名
    BUSHI = 'BUSHI'  # 武士
    SHINTO = 'SHINTO'  # 神主
    MONSTER = 'MONSTER'  # 妖怪


class FigureTypeSchema(v.Schema):
    name = v.SchemaNode(v.String(), validator=v.Length(1, 20))
    # image
    # ruleset

    @v.instantiate(missing=())
    class categories(v.SequenceSchema):
        category = v.SchemaNode(v.String(), validator=v.OneOf(c.value for c in FigureCategory))


class FigureType(config_repo.Model):
    yaml_tag = 'figure type'
    __pks__ = ('context', 'name')
    __schema__ = FigureTypeSchema()


class Figure(db_repo.Model):
    """
    * A figure can have more than one type, so `types = List`
    * `location == None` means the figure is out of game
    """
    __tablename__ = 'figure'
    __pks__ = ('context', 'id')

    id = Column(Integer, primary_key=True)
    type_name = Column(Unicode(20))
    location = Column(Unicode(20))
    owner_name = Column(Unicode(20), ForeignKey('clan.name'))
    controller_name = Column(Unicode(20), ForeignKey('clan.name'))

    owner = relationship("Clan", foreign_keys=[owner_name], backref='figures_owned')
    controller = relationship("Clan", foreign_keys=[controller_name], backref='figures_controlled')

    @reify
    def type(self):
        return config_repo.get("FigureType", (self.context, self.id))
