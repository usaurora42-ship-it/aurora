# encoding: utf-8
import yaml
from sqlalchemy.dialects.mysql import SMALLINT
from datetime import datetime

from app import db, logging
from app.model.validator import ModelValidator
from app.lib.util import Util


LOGGER = logging.getLogger(__name__)


class ModelCurrency(db.Model):
    __tablename__ = 'currencies'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'sqlite_autoincrement': True
    }

    id = db.Column(
        SMALLINT(unsigned=True),
        db.Sequence('currency_id_seq'),
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
        db.String(3),
        index=True,
        nullable=False
    )
    numeric_ref = db.Column(
        SMALLINT(unsigned=True)
    )
    date_create = db.Column(
        db.DECIMAL(15, 3),
        nullable=False,
        default=lambda : format(datetime.now().timestamp(), '.3f')
    )

    errors = None

    # Create Currency
    def create_currency(self, data):
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

    # Get ID Currency
    def get_currency_id(self, value):
        if not value:
            return None

        util = Util()

        currency_name = util.currency_lookup(value)
        if currency_name is None:
            return None

        query = ModelCurrency.query.with_entities(ModelCurrency.id).filter_by(
            name=currency_name
        )

        try:
            currency = query.first()
            return currency.id if currency else None
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
                keys.remove(e)

        result = util.get_dict(obj=obj, keys=keys)

        currency_model = ModelCurrency()
        result['asset'] = currency_model.get_representative_asset(result['alpha_3'])
        return result

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
            required: true
        numeric_ref:
            type: integer
            coerce: integer
            min: 0
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __repr__(self):
        return "<Currency %r>" % self.name
