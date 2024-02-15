# encoding: utf-8
import yaml
from datetime import datetime
from sqlalchemy.dialects.mysql import INTEGER

from app import db, logging
from app.model.validator import ModelValidator
from app.lib.util import Util

LOGGER = logging.getLogger(__name__)


class ModelLanguage(db.Model):
    __tablename__ = 'languages'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'sqlite_autoincrement': True
    }

    id = db.Column(
        INTEGER(unsigned=True),
        db.Sequence('language_id_seq'),
        primary_key=True,
        autoincrement=True,
        nullable=False
    )
    name = db.Column(
        db.String(40),
        unique=True,
        nullable=False
    )
    alpha_3 = db.Column(
        db.String(3)
    )
    date_create = db.Column(
        db.DECIMAL(15, 3),
        nullable=False,
        default=lambda : format(datetime.now().timestamp(), '.3f')
    )

    errors = None

    # Create Language
    def create_language(self, data):
        v = ModelValidator()
        if not v.validate(data, self.__val_create__()):
            self.errors = v.errors
            return None

        data = v.document

        exists = ModelLanguage.query.filter_by(name=data['name']).count()
        if exists > 0:
            return True

        # pop data partner
        for k in data:
            setattr(self, k, data[k])

        try:
            db.session.add(self)
            db.session.commit()
            return self
        except Exception as e:
            raise e

    # Get ID Language
    def get_language_id(self, value):
        if not value:
            return None

        util = Util()

        lang_name = util.language_lookup(value)
        if lang_name is None:
            return None

        query = ModelLanguage.query.with_entities(ModelLanguage.id).filter_by(
            name=lang_name
        )

        try:
            lang = query.first()
            return lang.id if lang else None
        except Exception as e:
            raise e

    # prepare response dict json
    def get_dict(obj, keys=None, exclude=[]):
        util = Util()

        # default keys
        if keys is None:
            keys = [
                'id', 'name', 'alpha_3'
            ]

        # exclude
        for e in exclude:
            if e in keys:
                keys.pop(e)

        return util.get_dict(obj=obj, keys=keys)

    # Validators
    def __val_create__(self):
        schema = '''
        name:
            type: string
            maxlength: 40
            required: true
        alpha_3:
            type: string
            maxlength: 3
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __repr__(self):
        return "<Language %r>" % self.name
