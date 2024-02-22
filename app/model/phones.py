# encoding: utf-8
import yaml
from datetime import datetime
from sqlalchemy.dialects.mysql import INTEGER

from app import db, logging
from app.model.enum import StatusEnum, PhoneTypeEnum, BooleanEnum
from app.model.validator import ModelValidator
from app.lib.util import Util

LOGGER = logging.getLogger(__name__)


class ModelPhone(db.Model):
    __tablename__ = 'phones'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'sqlite_autoincrement': True
    }

    id = db.Column(
        INTEGER(unsigned=True),
        db.Sequence('phone_id_seq'),
        primary_key=True,
        autoincrement=True,
        nullable=False
    )
    uuid = db.Column(
        db.String(36),
        unique=True,
        nullable=False
    )
    code_country = db.Column(
        db.String(4),
        nullable=False
    )
    code_area = db.Column(
        db.String(4),
        nullable=False
    )
    number = db.Column(
        db.String(15),
        nullable=False
    )
    type = db.Column(
        db.Enum(PhoneTypeEnum, validate_strings=True),
        default=PhoneTypeEnum.contact,
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

    errors = None

    # Create Phone
    def create_phone(self, data):
        v = ModelValidator()
        if not v.validate(data, self.__val_create__()):
            self.errors = v.errors
            return None

        data = v.document

        for k in data:
            setattr(self, k, data[k])

        try:
            db.session.add(self)
            db.session.commit()
            return self
        except Exception as e:
            raise e

    # Update Phone
    def update_phone(self, data):
        v = ModelValidator()
        if not v.validate(data, self.__val_update__()):
            self.errors = v.errors
            return None

        data = v.document

        phone_id = data.pop('id')
        phone = ModelPhone.query.filter_by(
            id=phone_id,
            status=StatusEnum.enabled
        ).first()

        if not phone:
            self.errors = {
                'phone': ['phone not found']
            }
            return None

        # check phone verified
        if phone.is_verified == BooleanEnum.true:
            self.errors = {
                'phone': ['this phone already verified, it cannot be updated']
            }
            return None

        # pop data phone
        for k in data:
            setattr(phone, k, data[k])

        try:
            db.session.commit()
            return phone
        except Exception as e:
            raise e

    # validators
    def __val_create__(self):
        schema = '''
        code_area:
            maxlength: 4
            required: true
            type: string
            coerce: str
        code_country:
            maxlength: 4
            required: true
            type: string
            coerce: str
        last_update:
            max: 999999999999
            min: 0
            type: number
            coerce: float
        number:
            maxlength: 15
            required: true
            type: string
            coerce: str
        type:
            allowed:
            - home
            - contact
            - comercial
            - mobile
            type: string
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __val_update__(self):
        schema = '''
        code_area:
            maxlength: 4
            type: string
            coerce: str
        code_country:
            maxlength: 4
            type: string
            coerce: str
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
        number:
            maxlength: 15
            type: string
            coerce: str
        type:
            allowed:
            - home
            - contact
            - comercial
            - mobile
            type: string
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __repr__(self):
        return "<Phone %r>" % self.id
