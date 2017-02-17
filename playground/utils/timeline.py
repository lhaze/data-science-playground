# -*- coding: utf-8 -*-
"""
# Sample timeline file content:
1500:
    alive_population: 5000
    mortality: 0.015
    _start:
        name: XV century
        wraith_conversion_factor: 0.2
1600:
    alive_population: 7000
1800:
    mortality: 0.006
"""
from collections import OrderedDict
from operator import itemgetter
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
        # import pdb; pdb.set_trace()
        return cls(sorted(description.items(), key=itemgetter(0)))

    def property(self, name):
        for tp, properties in self.items():
            if name in properties:
                yield (tp, properties[name])


class TimelineEvent(object):
    """An abstraction of an event."""


def show_example_timeline():
    from pprint import pprint
    tl = Timeline.read(__doc__)
    pprint(tl)
    print('alive_population: ', tuple(tl.property('alive_population')))
    print('alive_population: ', dict(tl.property('mortality')))


if __name__ == '__main__':
    show_example_timeline()
