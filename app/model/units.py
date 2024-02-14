# encoding: utf-8
import yaml
from sqlalchemy.dialects.mysql import SMALLINT
from datetime import datetime

from app import db, logging
from app.model.validator import ModelValidator
from app.lib.util import Util

LOGGER = logging.getLogger(__name__)


class ModelUnit(db.Model):
    __tablename__ = 'units'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'sqlite_autoincrement': True
    }

    id = db.Column(
        SMALLINT(unsigned=True),
        db.Sequence('unit_id_seq'),
        primary_key=True,
        autoincrement=True,
        nullable=False
    )
    description = db.Column(
        db.String(40),
        unique=True,
        nullable=False
    )    

    errors = None

    # Create Unit
    def create_unit(self, data):
        v = ModelValidator()
        if not v.validate(data, self.__val_create__()):
            self.errors = v.errors
            return None

        data = v.document

        # pop data
        for k in data:
            setattr(self, k, data[k])

        try:
            db.session.add(self)
            db.session.commit()
            return self
        except Exception as e:
            raise e

    def get_unit_id(self, value):
        if not value:
            return None

        util = Util()

        unit_name = util.unit_lookup(value)
        if unit_name is None:
            return None

        query = ModelUnit.query.with_entities(ModelUnit.id).filter_by(
            name=unit_name
        )

        try:
            unit = query.first()
            return unit.id if unit else None
        except Exception as e:
            raise e

    # prepare response dict json
    def get_dict(obj, keys=None, exclude=[]):
        util = Util()

        # default keys
        if keys is None:
            keys = [
                'id', 'description'
            ]

        # exclude
        for e in exclude:
            if e in keys:
                keys.remove(e)

        return util.get_dict(obj=obj, keys=keys)

    # Validators
    def __val_create__(self):
        schema = '''
        description:
            type: string
            maxlength: 40
            required: true        
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __repr__(self):
        return "<Unit %r>" % self.name
