# -*- coding: utf-8 -*-
import typing as t

from colander import *  # noqa
from colanderalchemy.schema import SQLAlchemySchemaNode  # noqa

from .imports import import_entity


# importing whole colander here is a way to:
# * abstractize from the dependency on colander implementation of schemas (we might need some shims)
# * gather schema classes from other packages (ie. ColanderAlchemy) in one place
# * add own SchemaTypes (ie. Instance)
class Instance(SchemaType):

    def __init__(self, klass: t.Union[t.Type, str]):
        self.klass = klass

    def _get_klass(self) -> None:
        if isinstance(self.klass, str):
            self.klass = import_entity(self.klass)
            assert self.klass.__schema__, "Class %r has no __schema__ provided" % self.klass

    def serialize(self, node: SchemaNode, appstruct: Any) -> t.Union[dict, null.__class__]:
        self._get_klass()
        if appstruct is null:
            return null
        if not isinstance(appstruct, self.klass):
            raise Invalid(node, '%r is not an instance of %r' % (appstruct, self.klass))
        return self.klass.__schema__.serialize(appstruct)

    def deserialize(self, node: SchemaNode, cstruct: dict) -> t.Any:
        self._get_klass()
        if cstruct is null:
            return null
        if isinstance(cstruct, self.klass):
            instance = cstruct
        elif isinstance(cstruct, dict):
            instance = self.klass(**cstruct)
        else:
            raise Invalid(node, (
                '%r has to be an instance of %r or a serialized form it' % (cstruct, self.klass)
            ))
        return instance
