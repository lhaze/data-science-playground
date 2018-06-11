# -*- coding: utf-8 -*-
from sqlalchemy import Column, ForeignKey, Integer, Unicode
from sqlalchemy.orm import relationship

from rising_sun import db_repo


class Game(db_repo.Model):
    __tablename__ = 'game'
    __pks__ = ('context', 'id')

    id = Column(Integer, primary_key=True)
    config = Column(Unicode(20))

    def resolve(self, action: dict):
        pass
