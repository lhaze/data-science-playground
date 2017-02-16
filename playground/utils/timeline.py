# -*- coding: utf-8 -*-
"""
# Sample timeline file content:
1500:
    alive_population: 5000
    mortality: 0.015
    _start:
        name: XV century
        wraith_conversion_factor: 0.2
"""
from collections import OrderedDict
import yaml


class Timeline(OrderedDict):
    """
    An abstraction over a sequence of timepoints & events, both of which
    have properties.
    """

    @classmethod
    def load(cls, filename):
        with open(filename) as file:
            description = yaml.load(file)
        return cls.create(description)

    @classmethod
    def read(cls, string):
        description = yaml.load(string)
        return cls.create(description)

    @classmethod
    def create(cls, description):
        return cls(description)  # TODO


class TimelineEvent(object):
    """An abstraction of an event."""


def load_example_timeline():
    from pprint import pprint
    pprint(Timeline.read(__doc__))


if __name__ == '__main__':
    load_example_timeline()
