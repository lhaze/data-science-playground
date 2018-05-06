# -*- coding: utf-8 -*-
from rising_sun import config_repo, db_repo  # noqa
from rising_sun.models import Game


new_game = Game(context='context', id='id')
db_repo.add(new_game)

existing_game = db_repo.get('Game', ('context', 'id'))
