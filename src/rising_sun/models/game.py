# -*- coding: utf-8 -*-
from rising_sun.models.base import BaseModel


class Game(BaseModel):

    @classmethod
    def build_from_yaml(cls, filepath):
        board = cls.build_board(filepath)
        return Game(board=board)

    @classmethod
    def build_board(cls, filepath):
        return None
