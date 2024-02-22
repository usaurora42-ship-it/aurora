# encoding: utf-8
import yaml
from datetime import datetime
from sqlalchemy.dialects.mysql import SMALLINT, INTEGER

from app import db, logging
from app.model.enum import StatusEnum, AddressTypeEnum, BooleanEnum
from app.model.validator import ModelValidator
from app.lib.util import Util

LOGGER = logging.getLogger(__name__)


class ModelAddress(db.Model):
    __tablename__ = 'addresses'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'sqlite_autoincrement': True
    }

    id = db.Column(
        INTEGER(unsigned=True),
        db.Sequence('address_id_seq'),
        primary_key=True,
        autoincrement=True,
        nullable=False
    )
    uuid = db.Column(
        db.String(36),
        unique=True,
        nullable=False
    )
    country_id = db.Column(
        INTEGER(unsigned=True),
        db.ForeignKey('countries.id', onupdate='CASCADE'),
        nullable=False
    )
    name = db.Column(
        db.String(20),
        nullable=False
    )
    state = db.Column(
        db.String(50),
        nullable=False
    )
    city = db.Column(
        db.String(60),
        nullable=False
    )
    district = db.Column(
        db.String(50),
        nullable=False
    )
    zip_code = db.Column(
        db.String(20),
        nullable=False
    )
    street = db.Column(
        db.String(80),
        nullable=False
    )
    street_number = db.Column(
        db.String(20),
        nullable=False
    )
    complement = db.Column(
        db.String(30)
    )
    type = db.Column(
        db.Enum(AddressTypeEnum, validate_strings=True),
        default=AddressTypeEnum.contact,
        server_default='contact'
    )
    is_verified = db.Column(
        db.Enum(BooleanEnum, validate_strings=True),
        default=BooleanEnum.false,
        server_default='false'
    )
    status = db.Column(
        db.Enum(StatusEnum, validate_strings=True),
        default=StatusEnum.enabled,
        server_default='enabled',
        index=True
    )
    last_update = db.Column(
        db.DECIMAL(15, 3),
        nullable=False,
        default=lambda : format(datetime.now().timestamp(), '.3f'),
        onupdate=lambda: format(datetime.now().timestamp(), '.3f')
    )
    date_create = db.Column(
        db.DECIMAL(15, 3),
        nullable=False,
        default=lambda : format(datetime.now().timestamp(), '.3f')
    )

    ## relationship
    country = db.relationship(
        'ModelCountry',
        backref=db.backref('address_country', lazy=True)
    )

    errors = None

    # Create Address
    def create_address(self, data):
        v = ModelValidator()
        if not v.validate(data, self.__val_create__()):
            self.errors = v.errors
            return None

        data = v.document

        ## gambi anti burrice
        if 'complement' in data and data['complement'] == 'null':
            data['complement'] = None

        for k in data:
            setattr(self, k, data[k])

        try:
            db.session.add(self)
            db.session.commit()
            return self
        except Exception as e:
            raise e

    # Update Address
    def update_address(self, data):
        v = ModelValidator()
        if not v.validate(data, self.__val_update__()):
            self.errors = v.errors
            return None

        data = v.document

        address_id = data.pop('id')
        address = ModelAddress.query.filter_by(
            id=address_id,
            status=StatusEnum.enabled
        ).first()

        if not address:
            self.errors = {
                'address': ['address not found']
            }
            return None

        ## gambi anti burrice
        if 'complement' in data and data['complement'] == 'null':
            data['complement'] = None

        # pop data address
        for k in data:
            setattr(address, k, data[k])

        try:
            db.session.commit()
            return address
        except Exception as e:
            raise e

    # prepare response dict json
    def get_dict(obj, keys=None, exclude=[]):
        util = Util()

        # default keys
        if keys is None:
            keys = [
                'id', 'city', 'complement', 'name', 'state', 'district',
                'street', 'street_number', 'type', 'zip_code', 'is_verified'
            ]

        # exclude
        for e in exclude:
            if e in keys:
                keys.pop(e)

        return util.get_dict(obj=obj, keys=keys)

    # validator
    def __val_create__(self):
        schema = '''
        city:
            maxlength: 60
            required: true
            type: string
        complement:
            maxlength: 30
            type: string
        district:
            maxlength: 50
            required: true
            type: string
        country_id:
            max: 65535
            min: 1
            required: true
            type: integer
            coerce: integer
        last_update:
            max: 999999999999
            min: 0
            type: number
            coerce: float
        name:
            maxlength: 20
            required: true
            type: string
        state:
            maxlength: 50
            required: true
            type: string
        street:
            maxlength: 80
            required: true
            type: string
        street_number:
            maxlength: 20
            required: true
            type: string
            coerce: str
        type:
            allowed:
            - home
            - contact
            - comercial
            type: string
        zip_code:
            maxlength: 20
            required: true
            type: string
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __val_update__(self):
        schema = '''
        city:
            maxlength: 60
            type: string
        complement:
            maxlength: 30
            type: string
        district:
            maxlength: 50
            type: string
        country_id:
            max: 65535
            min: 1
            type: integer
            coerce: integer
        id:
            min: 1
            required: true
            type: integer
            coerce: integer
        last_update:
            max: 999999999999
            min: 0
            type: number
            coerce: float
        name:
            maxlength: 20
            type: string
        state:
            maxlength: 50
            type: string
        street:
            maxlength: 80
            type: string
        street_number:
            maxlength: 20
            type: string
            coerce: str
        type:
            allowed:
            - home
            - contact
            - comercial
            type: string
        zip_code:
            maxlength: 20
            type: string
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __repr__(self):
        return "<Address %r>" % self.name
