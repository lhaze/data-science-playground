# -*- coding: utf-8 -*-

from rising_sun.model.base import Instance, Model


class Clan(Model):
    symbol = Instance(str, required=True)
    name = Instance(str, required=True)

    @classmethod
    def sample(cls):
        return [
            cls(symbol='L', name='Lotus'),
            cls(symbol='K', name='Koi'),
        ]
