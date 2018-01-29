from builtins import int, list, open, range, sorted, sum, zip
from functools import lru_cache
import numpy as np

from utils.timeline import Timeline
from utils.interpolations import build_interpolation


# timeline = Timeline.load('how_many_wraiths_timeline.yaml')
# START_YEAR = timeline.start
# END_YEAR = timeline.end
# year_list = list(range(START_YEAR, END_YEAR + 1))



def alive_population(t):
    """(Alive) population of Warsaw, based on demographical data ([1], [2])"""
    return int(np.interp(t, *alive_population_datapoints))


def mortality_rate(t):
    """Very simple approach to estimate mortality"""
    return 0.01  # if is_peaceful(t) else 1


@lru_cache(maxsize=None)
def population_per_dod(t, dod):
    if t < START_YEAR:
        return 0
    if t == dod:
        return int(natural_growth(t) * enfant_survavibility_factor(t))
    return int(population_per_dod(t - 1, dod) * (1 - pass_away_factor(t) + migration_factor(t)))


def pass_away_factor(t):
    return 0


def migration_factor(t):
    return 0


def population(t):
    return sum(population_per_dod(t, dod) for dod in range(START_YEAR, t + 1))


def natural_growth(t):
    return int(alive_population(t) * mortality_rate(t) * wraith_turn_factor(t))


def wraith_turn_factor(t):
    return 0.2


def enfant_survavibility_factor(t):
    rate = 1 - enfant_oblivion_rate(t) - enfant_decorpsing_rate(t)
    return rate if rate > 0 else 0


def enfant_oblivion_rate(t):
    return 0.1


def enfant_decorpsing_rate(t):
    return 0.1


def pass_away_rate(t):
    rate = senior_oblivion_rate(t) + senior_ascension_rate(t) + senior_decorpsing_rate(t)
    return rate if rate < 1 else 1


def senior_oblivion_rate(t):
    return 0.02


def senior_ascension_rate(t):
    return 0.01


def senior_decorpsing_rate(t):
    return 0.01
