# -*- coding: utf-8 -*-
from itertools import tee
from typing import (
    Any,
    Iterable,
    Callable,
    NewType,
    Sequence,
    Union,
)

Argument = NewType('Argument', Any)
Value = NewType('Value', Any)
Function = Callable[[Union[Argument, Sequence[Argument]]], Value]


def transpose(items: Iterable) -> list:
    """
    Transforms iterable of datapoints into vectors of arguments and values.

    >>> transpose([(1, 1), (2, 2), (3, 3)])
    [(1, 2, 3), (1, 2, 3)]
    """
    return list(zip(*items))


def pairwise(iterable):
    """
    Returns iterator that iterates over pairs of adjacent elements of given
    iterable.

    >>> list(pairwise([1, 2, 3, 4]))
    [(1, 2), (2, 3), (3, 4)]
    """
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def extended_to_sequence_of_inputs(f):
    """
    Extends given function to return generator of return values iff it is
    given an iterable of inputs.
    """
    def wrapper(t):
        if isinstance(t, Iterable):
            return (f(v) for v in t)
        return f(t)

    return wrapper
