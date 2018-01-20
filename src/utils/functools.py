# -*- coding: utf-8 -*-
from itertools import tee
import numpy as np
from typing import (
    Any,
    Iterable,
    Callable,
    Mapping,
    NewType,
    Optional,
    Sequence,
    Union,
)

from utils.timeline import Timeline, TimelineIndex


Value = NewType('Value', Any)
Argument = NewType('Argument', Any)
Function = Callable[[Union[Argument, Sequence[Argument]]], Value]


def transpose(items: Iterable) -> list:
    """
    Transforms iterable of datapoints into vectors of

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


def _disconnect_timespans(datapoints: Iterable) -> Iterable:
    """
    Generator that returns non-overlaping ephemeral datapoints by seperation
    of its TimelineIndexes.
    >>> datapoints = [
    ...     (TimelineIndex((1, 5)), 1),
    ...     (TimelineIndex((2, 4)), 2),
    ...     (TimelineIndex((2, 3)), 3),
    ...     (TimelineIndex((6, 6)), 4),
    ... ]
    >>> list(_disconnect_timespans(datapoints))
    [(1, 1), ((2, 3), 3), (4, 2), (6, 6)]
    """
    for current_dp, next_dp in pairwise(datapoints):
        current_index, value = current_dp
        new_indexes = current_index - next_dp[0]
        yield from ((new_index, value) for new_index in new_indexes)


def _build_ephemeral_dict(datapoints: Iterable) -> Optional[Mapping]:
    """
    Builds a dict that defines all ephemeral values, based on an iterable of
    ephemeral datapoints.

    NB: asserts that datapoints are sorted

    TODO: thus function accepts t only of int type for now; if you want
    generalization of input types, rewrite it retaining Mapping interface
    of return value.

    >>> datapoints = [
    ...     (TimelineIndex((1, 5)), 1),
    ...     (TimelineIndex((2, 4)), 2),
    ...     (TimelineIndex((2, 3)), 3),
    ...     (TimelineIndex((6, 6)), 4),
    ... ]
    >>> _build_ephemeral_dict(datapoints)
    {1: 1, 2: 3, 3: 3, 4: 2, 5: 1, 6: 6}
    """
    # for current_dp, next_dp in pairwise(datapoints):
    starts, ends = transpose(dp if isinstance(dp, Iterable) else (dp, None) for dp in datapoints)
    return {}


def _build_ephemeral_aspect(datapoints: Iterable, interpolation: Function):
    """
    Wraps `interpolation` with a function that overrides interpolation when
    ephemeral values are specified.

    >>> @extended_to_sequence_of_inputs
    ... def interpolation(t):
    ...     return t + 0.5

    """
    ephemeral = _build_ephemeral_dict(datapoints)
    if ephemeral:

        def ephemeral_wrapper(t):
            if t in ephemeral:
                # ephemeral case, return its value
                return ephemeral[t]
            # regular case, no ephemeral for this value, compute interpolation
            return interpolation(t)
    else:
        ephemeral_wrapper = interpolation

    return ephemeral_wrapper


def _build_cast_aspect(cast: Function, interpolation: Function):
    """
    Wraps `interpolation` function with `cast` function. Respects
    the value vs. array of values duality.

    >>> @extended_to_sequence_of_inputs
    ... def interpolation(t):
    ...     return t + 0.5
    >>> casted = _build_cast_aspect(int, interpolation)
    >>> casted(0)
    0
    >>> casted(42)
    42
    >>> list(casted((0, 42)))
    [0, 42]
    """
    @extended_to_sequence_of_inputs
    def casting_wrapper(t: Argument):
        result = interpolation(t)
        return cast(result)

    return casting_wrapper


def build_interpolation(tl: Timeline, name: str, cast=None) \
        -> Function:
    """
    Returns interpolation of a property (specified by its name), based on
    given Timeline.

    Interpolation is a function of timepoint or a sequence of timepoints. It
    returns a value at the timepoint in the former case or a sequence of
    values in the latter one.

    If the property is covered by ephemeral(s), value for is taken from the
    most specific ephemeral.
    """
    regular_datapoints, ephemeral_datapoints = tl.property_lists(name)
    interpolation_vectors = transpose(regular_datapoints)

    def interpolation(t):
        return np.interp(t, *interpolation_vectors)

    if cast:
        interpolation = _build_cast_aspect(cast, interpolation)

    if ephemeral_datapoints:
        interpolation = _build_ephemeral_aspect(ephemeral_datapoints, interpolation)

    return interpolation
