# -*- coding: utf-8 -*-
import json
import os
import typing as t

from ruamel import yaml


class ExtLoader(yaml.Loader):
    """YAML Loader with `!include` constructor."""

    def __init__(self, stream: t.IO, *args, **kwargs) -> None:
        """Initialise Loader."""
        try:
            self._root = os.path.split(stream.name)[0]
        except AttributeError:
            self._root = os.path.curdir

        super().__init__(stream, *args, **kwargs)


def construct_include(loader: ExtLoader, node: yaml.Node) -> t.Any:
    """Include file referenced at node."""

    filename = os.path.abspath(os.path.join(loader._root, loader.construct_scalar(node)))
    extension = os.path.splitext(filename)[1].lstrip('.')

    with open(filename, 'r') as f:
        if extension in ('yaml', 'yml'):
            return yaml.load(f, ExtLoader)
        elif extension in ('json', ):
            return json.load(f)
        else:
            return ''.join(f.readlines())


yaml.add_constructor('!include', construct_include, ExtLoader)


def load(stream: t.IO) -> t.Any:
    """
    Own YAML-deserialization based on:
        * ruamel.yaml (some additional bugfixes vs regular PyYaml module)
        * unsafe loading (be sure to use it only for own datafiles)
        * YAML inclusion feature
    """
    return yaml.load(stream, Loader=ExtLoader)


def load_from_filename(filename: t.Union[str, 'pathlib.Path']):
    with open(filename, 'r') as f:
        return load(f)
