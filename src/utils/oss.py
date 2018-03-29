# -*- coding: utf-8 -*-
import os


dirname = os.path.dirname


def path(filepath, *args):
    return os.path.abspath(os.path.join(filepath, *args))


def ensure_dir_exists(filepath):
    os.makedirs(filepath, exist_ok=True)
    return filepath
