# -*- coding: utf-8 -*-
from functools import update_wrapper, lru_cache  # noqa
from typing import (
    Any,
    Callable,
    NewType,
    Sequence,
    Union,
)

from utils.itertools import is_sequence

Argument = NewType('Argument', Any)
Arguments = Union[Argument, Sequence[Argument]]
Value = NewType('Value', Any)
Function = Callable[[Arguments], Value]


def extended_to_sequence_of_inputs(f: Function):
    """
    Extends given function to return generator of return values iff it is
    given an iterable of inputs.
    """
    def wrapper(t: Arguments):
        if is_sequence(t):
            return (f(v) for v in t)
        return f(t)

    return wrapper


class reify(object):
    """
    Copied from pyramid.decorator:reify

    Use as a class method decorator.  It operates almost exactly like the
    Python ``@property`` decorator, but it puts the result of the method it
    decorates into the instance dict after the first call, effectively
    replacing the function it decorates with an instance variable.  It is, in
    Python parlance, a non-data descriptor.  The following is an example and
    its usage:
    .. doctest::
        >>> from utils.functools import reify
        >>> class Foo(object):
        ...     @reify
        ...     def jammy(self):
        ...         print('jammy called')
        ...         return 1
        >>> f = Foo()
        >>> v = f.jammy
        jammy called
        >>> print(v)
        1
        >>> f.jammy
        1
        >>> # jammy func not called the second time; it replaced itself with 1
        >>> # Note: reassignment is possible
        >>> f.jammy = 2
        >>> f.jammy
        2
    """
    def __init__(self, wrapped):
        self.wrapped = wrapped
        update_wrapper(self, wrapped)

    def __get__(self, inst, objtype=None):
        if inst is None:
            return self
        val = self.wrapped(inst)
        setattr(inst, self.wrapped.__name__, val)
        return val
