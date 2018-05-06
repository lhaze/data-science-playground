# -*- coding: utf-8 -*-
from sqlalchemy import Column, ForeignKey, Integer, Unicode
from sqlalchemy.orm import relationship

from rising_sun.models.base import DbModel


class Game(DbModel):
    __tablename__ = 'game'
    __pks__ = ('context', 'id')

    id = Column(Integer, primary_key=True)
    config = Column(Unicode(20))

    @classmethod
    def build_from_yaml(cls, filepath):
        board = cls.build_board(filepath)
        return Game(board=board)

    @classmethod
    def build_board(cls, filepath):
        return None
