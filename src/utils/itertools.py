# -*- coding: utf-8 -*-
from collections import abc
from itertools import tee
from numpy import ndarray
from typing import Iterable, Sequence, Tuple


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
    >>> from datetime import date, timedelta
    >>> start = date(2017, 2, 1)
    >>> stop = date(2017, 2, 3)
    >>> step = timedelta(days=1)
    >>> list(xrange(start, stop, step))
    [datetime.date(2017, 2, 1), datetime.date(2017, 2, 2), datetime.date(2017, 2, 3)]
    >>> list(xrange(2.3, 7.5, 2.1))
    [2.3, 4.4, 6.5]
    """
    i = start
    while i <= stop:
        yield i
        i += step


generator_type = type(None for i in ())


def is_sequence(obj):
    """
    Checks whether `obj` is the real sequence, generator, tuple or list, etc and not
    a sequence-like object like dictionary or a string.

    >>> is_sequence([])
    True
    >>> is_sequence(())
    True
    >>> is_sequence(u'string')
    False
    >>> is_sequence(b'bytes')
    False
    >>> is_sequence({})
    False
    """
    return not isinstance(obj, (str, bytes, abc.Mapping)) and \
        isinstance(obj, (Sequence, generator_type, ndarray))


def recursive_get(obj, key, default=None):
    value = obj
    for fragment in key.split('.'):
        if isinstance(value, abc.Mapping):
            try:
                value = value.get(fragment)
            except KeyError:
                return default
        else:
            try:
                value = getattr(value, fragment)
            except AttributeError:
                return default
    return value
