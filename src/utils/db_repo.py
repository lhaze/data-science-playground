# -*- coding: utf-8 -*-
import typing as t

from sqlalchemy import orm
from sqlalchemy.engine import create_engine, Engine
from sqlalchemy.ext.declarative.api import declarative_base, DeclarativeMeta
from sqlalchemy.sql.schema import Table

from utils.functools import reify


class _QueryProperty(object):
    def __init__(self, sa):
        self.sa = sa

    def __get__(self, obj, type):
        try:
            mapper = orm.class_mapper(type)
            if mapper:
                return type.query_class(mapper, session=self.sa.session())
        except orm.exc.UnmappedClassError:
            return None


class DbRepo:

    def __init__(self,
                 app=None,
                 session_options=None,
                 metadata=None,
                 query_class=orm.Query,
                 model=object,
                 metaclass=DeclarativeMeta,
                 debug: bool = False,
                 db_url: str = 'sqlite://'
                 ):
        self.app = app
        self._debug = debug
        self._db_url = db_url
        self._class_registry = {}
        self.Query = query_class
        self.session = self.create_scoped_session(session_options)
        self.Model = self.make_declarative_base(model, metaclass, metadata)

    @property
    def metadata(self):
        return self.Model.metadata

    def create_scoped_session(self, scopefunc=None, options=None):
        """Create a :class:`~sqlalchemy.orm.scoping.scoped_session`
        on the factory from :meth:`create_session`.

        :param scopefunc: an extra key ``'scopefunc'`` can be given to
        specify a custom scope function.  If it's not provided, Flask's app
        context stack identity is used. This will ensure that sessions are
        created and removed with the request/response cycle, and should be fine
        in most cases.

        :param options: dict of keyword arguments passed to session class  in
            ``create_session``
        """
        options = options or {}
        options.setdefault('query_cls', self.Query)
        return orm.scoped_session(
            self.create_session(options), scopefunc=scopefunc
        )

    def create_session(self, options):
        """Create the session factory used by :meth:`create_scoped_session`.

        The factory **must** return an object that SQLAlchemy recognizes as a session,
        or registering session events may raise an exception.

        Valid factories include a :class:`~sqlalchemy.orm.session.Session`
        class or a :class:`~sqlalchemy.orm.session.sessionmaker`.

        :param options: dict of keyword arguments passed to session class
        """
        return orm.sessionmaker(db=self, **options)

    def make_declarative_base(self, model=object, metaclass=DeclarativeMeta, metadata=None):
        """Creates the declarative base that all models will inherit from.

        :param model: base model class (or a tuple of base classes) to pass
            to :func:`~sqlalchemy.ext.declarative.declarative_base`. Or a class
            returned from ``declarative_base``, in which case a new base class
            is not created.
        :param metadata: :class:`~sqlalchemy.MetaData` instance to use, or
            none to use SQLAlchemy's default.
        :param metaclass:
        """
        if not isinstance(model, DeclarativeMeta):
            model = declarative_base(
                bind=self.engine,
                cls=model,
                name='DbModel',
                metadata=metadata,
                metaclass=metaclass,
                class_registry=self._class_registry
            )

        # if user passed in a declarative base and a metaclass for some reason,
        # make sure the base uses the metaclass
        if metadata is not None and model.metadata is not metadata:
            model.metadata = metadata

        if not getattr(model, 'query_class', None):
            model.query_class = self.Query

        model.query = _QueryProperty(self)
        return model

    @reify
    def engine(self) -> Engine:
        if self._debug:
            engine = create_engine(
                self._db_url,
                convert_unicode=True,
                echo=True,
                # connect_args={'check_same_thread': False}
            )
        else:
            engine = create_engine(self._db_url, convert_unicode=True)
        return engine

    def create_tables(self, drop: bool = False) -> t.Mapping[str, Table]:
        metadata = self.Model.metadata
        if drop:
            metadata.drop_all()
        metadata.create_all()
        return metadata.tables

    def add(self, instance: 'Model', commit: bool = True):
        session = instance.metadata.session
        session.add(instance)
        if commit:
            session.commit()

    def get(self, klass_name: str, pk: t.Any):
        klass = self._class_registry.get(klass_name)
        assert klass, f"No class named '{klass_name}' found"
        return klass.query.get(pk)
