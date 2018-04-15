# -*- coding: utf-8 -*-
import pytest

from ..board import *


@pytest.fixture(scope='session')
def regions():
    return [
        Region(name='a', reward={}),
        Region(name='b', reward={}),
    ]


def test_connection_str(regions):
    assert repr(Connection(a=regions[0], b=regions[1])) == "Connection(None, a, b)"


def test_connection_error_same_region(regions):
    with pytest.raises(v.Invalid):
        Connection(a=regions[0], b=regions[0])


def test_connection_symmetric(regions):
    c12 = Connection(a=regions[0], b=regions[1])
    c21 = Connection(a=regions[0], b=regions[1])
    assert c12 == c21
