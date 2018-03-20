# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, ForeignKey

from rising_sun.model.base import Model


class Clan(Model):
    symbol = Column(String(2), primary_key=True)
    name = Column(String(50))

    def __repr__(self):
        return f"族({self.name})"

    @classmethod
    def sample(cls):
        """
        >>> Clan.sample()
        [族(Lotus), 族(Koi)]
        """
        return [
            cls(symbol='L', name='Lotus'),
            cls(symbol='K', name='Koi'),
        ]

    @classmethod
    def test(cls):
        """
        >>> Clan.test()
        >>> Clan.session.query(Clan).all()
        [族(Lotus), 族(Koi)]
        """
        [cls.session.add(c) for c in cls.sample()]
        cls.session.commit()
