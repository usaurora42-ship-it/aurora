# encoding: utf-8
import yaml
from datetime import datetime
from sqlalchemy.dialects.mysql import INTEGER

from app import db, logging
from app.model.validator import ModelValidator
from app.model.enum import StatusEnum, AddressTypeEnum, BooleanEnum
from app.lib.util import Util

LOGGER = logging.getLogger(__name__)


class ModelPartner(db.Model):
    __tablename__ = 'partners'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'sqlite_autoincrement': True
    }

    id = db.Column(
        INTEGER(unsigned=True),
        db.Sequence('partner_id_seq'),
        primary_key=True,
        autoincrement=True,
        nullable=False
    )
    country_id = db.Column(
        INTEGER(unsigned=True),
        db.ForeignKey('countries.id', onupdate='CASCADE'),
        nullable=False
    )
    language_id = db.Column(
        INTEGER(unsigned=True),
        db.ForeignKey('languages.id', onupdate='CASCADE'),
        nullable=False
    )
    uuid = db.Column(
        db.String(36),
        unique=True,
        nullable=False
    )
    name = db.Column(
        db.String(80),
        nullable=False
    )
    segment = db.Column(
        db.String(80),
        nullable=False
    )
    email = db.Column(
        db.String(50),
        unique=True
    )
    password = db.Column(
        db.String(28)
    )
    timezone = db.Column(
        db.String(40),
        default='America/Sao_Paulo',
        server_default='America/Sao_Paulo'
    )
    avatar_path = db.Column(
        db.Text
    )
    extra_data = db.Column(
        db.JSON,
        comment='json extra data'
    )
    status = db.Column(
        db.Enum(StatusEnum, validate_strings=True),
        server_default='enabled',
        default=StatusEnum.enabled,
        index=True
    )
    ip = db.Column(
        db.String(39),
        nullable=False,
        comment='ip address used in signup'
    )
    date_create = db.Column(
        db.DECIMAL(15, 3),
        nullable=False,
        default=lambda : format(datetime.now().timestamp(), '.3f')
    )

    # relationship
    country = db.relationship(
        'ModelCountry',
        backref=db.backref('partner_country', lazy=True)
    )

    language = db.relationship(
        'ModelLanguage',
        backref=db.backref('partner_language', lazy=True)
    )

    errors = None

    # Create Partner
    def create_partner(self, data):
        v = ModelValidator()
        if not v.validate(data, self.__val_create__()):
            self.errors = v.errors
            return None

        data = v.document

        # if exists
        exists = self.query.filter_by(email=data['email']).first()
        if exists:
            return exists

        # pop data partner
        for k in data:
            setattr(self, k, data[k])

        util = Util()
        self.uuid = util.gen_uuid()

        if 'password' in data:
            self.password = util.encrypt_password(data['password'])
            self.status = StatusEnum.enabled

        try:
            db.session.add(self)
            db.session.commit()
            return self
        except Exception as e:
            raise e

    # Update Partner
    def update_partner(self, data):
        v = ModelValidator()
        if not v.validate(data, self.__val_update__()):
            self.errors = v.errors
            return None

        data = v.document

        partner_id = data.pop('id')
        partner = ModelPartner.query.filter_by(
            id=partner_id,
            status=StatusEnum.enabled
        ).first()

        if not partner:
            self.errors = {
                'partner': ['partner not found']
            }
            return None

        # pop data partner
        for k in data:
            setattr(partner, k, data[k])

        try:
            db.session.commit()
            return partner
        except Exception as e:
            raise e

    # Update Password
    def update_password(self, data):
        v = ModelValidator()
        if not v.validate(data, self.__val_password__()):
            self.errors = v.errors
            return None

        data = v.document

        partner = ModelPartner.query.filter_by(
            uuid=data['partner_uuid'],
            status=StatusEnum.enabled
        ).first()

        if not partner:
            self.errors = {
                'partner': ['partner not found']
            }
            return None

        util = Util()
        partner.password = util.encrypt_password(data['password'])

        try:
            db.session.commit()
            return partner
        except Exception as e:
            raise e

    # prepare response dict json
    def get_dict(obj, keys=None, exclude=[]):
        # default keys
        if keys is None:
            keys = [
                'uuid', 'name', 'email', 'timezone', 'theme', 'url_logo', 'extra_data'
            ]

        # exclude
        for e in exclude:
            if e in keys:
                keys.pop(e)

        util = Util()
        return util.get_dict(obj=obj, keys=keys)

    # Validators
    def __val_create__(self):
        schema = '''
        avatar_path:
            type: string
        country_id:
            coerce: integer
            max: 65535
            min: 1
            required: true
            type: integer
        email:
            maxlength: 50
            type: string
            check_with: email
        extra_data:
            check_with: json
        ip:
            maxlength: 39
            required: true
            type: string
        language_id:
            coerce: integer
            max: 65535
            min: 1
            required: true
            type: integer
        name:
            maxlength: 80
            required: true
            type: string
        password:
            type: string
        timezone:
            maxlength: 40
            type: string
            check_with: timezone
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __val_update__(self):
        schema = '''
        avatar_path:
            type: string
        country_id:
            coerce: integer
            max: 65535
            min: 1
            type: integer
        email:
            maxlength: 50
            type: string
            check_with: email
        robobanker_client_id:
            maxlength: 36
            minlength: 36
            type: string
        robobanker_api_key:
            maxlength: 27
            minlength: 27
            type: string
        extra_data:
            check_with: json
        id:
            min: 1
            required: true
            type: integer
        language_id:
            coerce: integer
            max: 65535
            min: 1
            type: integer
        name:
            maxlength: 80
            type: string
        password:
            type: string
        timezone:
            maxlength: 40
            type: string
            check_with: timezone
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __val_password__(self):
        schema = '''
        partner_uuid:
            type: string
            required: true
            maxlength: 36
            minlength: 36
        password:
            type: string
            required: true
            coerce: str
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __repr__(self):
        return "<Partner %r>" % self.name