# -*- coding: utf-8 -*-
from itertools import tee
from typing import Iterable, Tuple


def transpose(items: Iterable) -> list:
    """
    Transforms iterable of datapoints into vectors of arguments and values.

    >>> transpose([(1, 1), (2, 2), (3, 3)])
    [(1, 2, 3), (1, 2, 3)]
    """
    return list(zip(*items))


def pairwise(iterable: Iterable) -> Iterable[Tuple[Iterable, Iterable]]:
    """
    Returns iterator that iterates over pairs of adjacent elements of given
    iterable.

    >>> list(pairwise([1, 2, 3, 4]))
    [(1, 2), (2, 3), (3, 4)]
    """
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def xrange(start, stop, step):
    """
    Naive range iterator, which can support Numbers other than int
    and date & datetime objects.

    NB: stop point is included!
    """
    i = start
    while i <= stop:
        yield i
        i += step
