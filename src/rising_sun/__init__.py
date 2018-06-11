# -*- coding: utf-8 -*-
from utils.db_repo import DbRepo

from . import config_repo
from .base_model import DbModelBase, DbModelMeta


db_repo = DbRepo(model=DbModelBase, metaclass=DbModelMeta)
config = config_repo
