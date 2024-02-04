# encoding: utf-8
import yaml
from sqlalchemy.dialects.mysql import SMALLINT
from datetime import datetime

from app import db, logging
from app.model.validator import ModelValidator
from app.lib.util import Util

LOGGER = logging.getLogger(__name__)


class ModelCountry(db.Model):
    __tablename__ = 'countries'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'sqlite_autoincrement': True
    }

    id = db.Column(
        SMALLINT(unsigned=True),
        db.Sequence('country_id_seq'),
        primary_key=True,
        autoincrement=True,
        nullable=False
    )
    name = db.Column(
        db.String(40),
        unique=True,
        nullable=False
    )
    official_name = db.Column(
        db.String(60)
    )
    alpha_2 = db.Column(
        db.String(2)
    )
    alpha_3 = db.Column(
        db.String(3),
        index=True,
        nullable=False
    )
    numeric_ref = db.Column(
        SMALLINT(unsigned=True),
        nullable=False,
        index=True
    )
    date_create = db.Column(
        db.DECIMAL(15, 3),
        nullable=False,
        default=lambda : format(datetime.now().timestamp(), '.3f')
    )

    country_factor = db.relationship('ModelCountryFactor', uselist=False, primaryjoin='ModelCountryFactor.country_id == ModelCountry.id', viewonly=True)

    errors = None

    # Create Country
    def create_country(self, data):
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

    def get_country_id(self, value):
        if not value:
            return None

        util = Util()

        country_name = util.country_lookup(value)
        if country_name is None:
            return None

        query = ModelCountry.query.with_entities(ModelCountry.id).filter_by(
            name=country_name
        )

        try:
            country = query.first()
            return country.id if country else None
        except Exception as e:
            raise e

    # prepare response dict json
    def get_dict(obj, keys=None, exclude=[]):
        util = Util()

        # default keys
        if keys is None:
            keys = [
                'id', 'name', 'official_name', 'alpha_3'
            ]

        # exclude
        for e in exclude:
            if e in keys:
                keys.remove(e)

        return util.get_dict(obj=obj, keys=keys)

    # Validators
    def __val_create__(self):
        schema = '''
        name:
            type: string
            maxlength: 40
            required: true
        official_name:
            type: string
            maxlength: 60
        alpha_2:
            type: string
            maxlength: 2
        alpha_3:
            type: string
            maxlength: 3
            required: true
        numeric_ref:
            type: integer
            coerce: integer
            min: 0
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __repr__(self):
        return "<Country %r>" % self.name
