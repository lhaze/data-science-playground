#!/usr/bin/env python3
from setuptools import setup, find_packages
# from setuptools.command.test import test as TestCommand


NAME = 'data-science-playground'
VERSION = (0, 0, 1, 'dev')
INSTALL_REQUIRES = ()
TESTS_REQUIRE = (
    'pytest',
)
SETUP_REQUIRE = (
    'pytest-runner',
)


if __name__ == '__main__':
    setup(
        name=NAME,
        version='.'.join(str(i) for i in VERSION),
        install_requires=INSTALL_REQUIRES,
        tests_require=TESTS_REQUIRE,
        setup_requires=SETUP_REQUIRE,
        packages=find_packages(),
    )
