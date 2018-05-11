# -*- coding: utf-8 -*-
from rising_sun import db_repo
from rising_sun.models import Game


def create_example_setup():
    db_repo.create_tables()
    new_game = Game(context='context', id='id')
    db_repo.add(new_game)


def get_action(request):
    return {
        'type': 'foo',
        'some': 'arg',
    }


def build_response(result):
    return result


def handle_example_request(request):
    game: Game = db_repo.get(Game, ('context', 'id'))
    action = get_action(request)
    result = game.resolve(action)
    return build_response(result)
