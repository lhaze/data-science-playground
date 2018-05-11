#!/usr/bin/env python
# -*- coding: utf-8 -*-
from rising_sun import handlers


if __name__ == '__main__':
    handlers.create_example_setup()
    print(handlers.handle_example_request({}))
