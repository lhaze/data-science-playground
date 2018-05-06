# -*- coding: utf-8 -*-
from utils.serialization import yaml

from rising_sun import config_repo, db_repo
from rising_sun.models import Game


def do_example_request():
    db_repo.create_tables()
    new_game = Game(context='context', id='id')
    db_repo.add(new_game)

    existing_game: Game = db_repo.get(Game, ('context', 'id'))
    print(yaml.dump(existing_game))
