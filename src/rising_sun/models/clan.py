# -*- coding: utf-8 -*-
from sqlalchemy import Column, Unicode
from sqlalchemy.orm import relationship

from rising_sun.models.base import DbModel


class Clan(DbModel):
    name = Column(Unicode(20), primary_key=True)
    # reserve = relationship("ClanReserve", uselist=False, back_populates="clan")
    __tablename__ = 'clan'
    _pk_key = 'name'

    @classmethod
    def sample(cls):
        """
        >>> Clan.sample()
        [Clan(Lotus), Clan(Koi)]
        """
        return [
            cls(name='Lotus'),
            cls(name='Koi'),
        ]

    @classmethod
    def test(cls):
        """
        >>> Clan.test()
        >>> Clan.query.all()
        [Clan(Lotus), Clan(Koi)]
        """
        [c.save() for c in cls.sample()]
