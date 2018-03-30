# -*- coding: utf-8 -*-
from sqlalchemy import Column, Unicode
from sqlalchemy.orm import relationship

from rising_sun.models.base import DbModel


class Clan(DbModel):
    symbol = Column(Unicode(2), primary_key=True)
    name = Column(Unicode(50), nullable=False)
    # reserve = relationship("ClanReserve", uselist=False, back_populates="clan")
    __tablename__ = 'clan'

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
        >>> Clan.query.all()
        [族(Lotus), 族(Koi)]
        """
        [c.save() for c in cls.sample()]
