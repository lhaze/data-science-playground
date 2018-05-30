# -*- coding: utf-8 -*-
import os
from pathlib import Path

dirname = os.path.dirname


def path(filepath, *args):
    return os.path.abspath(os.path.join(filepath, *args))


def ensure_dir_exists(filepath):
    os.makedirs(filepath, exist_ok=True)
    return filepath


def project_path_iter(repo_name='dsp'):
    for p in Path.cwd().parts:
        if p == repo_name:
            yield p
            return
        yield p


REPO_PATH = Path(*project_path_iter())
