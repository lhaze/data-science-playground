# -*- coding: utf-8 -*-
import json
import os
import typing as t

import colander as c
from colanderalchemy.schema import SQLAlchemySchemaNode
from ruamel import yaml

from .imports import import_entity


# importing whole colander here is a way to:
# * abstractize from the dependency on colander implementation of schemas (we might need some shims)
# * gather schema classes from other packages (ie. ColanderAlchemy) in one place
# * add own SchemaTypes (ie. Instance)
class Instance(c.SchemaType):

    def __init__(self, klass: t.Union[t.Type, str]):
        self.klass = klass

    def _get_klass(self) -> None:
        if isinstance(self.klass, str):
            self.klass = import_entity(self.klass)
            assert self.klass.__schema__, "Class %r has no __schema__ provided" % self.klass

    def serialize(self, node: c.SchemaNode, appstruct: t.Any) -> t.Union[dict, c._null]:
        self._get_klass()
        if appstruct is c.null:
            return c.null
        if not isinstance(appstruct, self.klass):
            raise c.Invalid(node, '%r is not an instance of %r' % (appstruct, self.klass))
        return self.klass.__schema__.serialize(appstruct)

    def deserialize(self, node: c.SchemaNode, cstruct: dict) -> t.Any:
        self._get_klass()
        if cstruct is c.null:
            return c.null
        if isinstance(cstruct, self.klass):
            instance = cstruct
        elif isinstance(cstruct, dict):
            instance = self.klass(**cstruct)
        else:
            raise c.Invalid(node, (
                '%r has to be an instance of %r or a serialized form it' % (cstruct, self.klass)
            ))
        return instance


c.SQLAlchemySchemaNode = SQLAlchemySchemaNode
c.Instance = Instance


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
