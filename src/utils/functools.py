# -*- coding: utf-8 -*-
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
