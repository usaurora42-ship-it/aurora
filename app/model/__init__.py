# encoding: utf-8
from sqlalchemy.orm import Query
from sqlalchemy.sql import visitors
from contextlib import suppress

def _has_entity(self, model):
    for visitor in visitors.iterate(self.statement):
        if visitor.__visit_name__ == 'binary':
            for vis in visitors.iterate(visitor):
                with suppress(AttributeError):
                    if model.__table__.fullname == vis.table.fullname:
                        return True
        if visitor.__visit_name__ == 'table':
            with suppress(TypeError):
                if model == visitor.entity_namespace:
                    return True
    return False

def unique_join(self, model, *args, **kwargs):
    if not self._has_entity(model):
        self = self.join(model, *args, **kwargs)
    return self

Query._has_entity = _has_entity
Query.unique_join = unique_join

from app.model.address import ModelAddress
