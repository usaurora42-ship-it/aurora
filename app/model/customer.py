# encoding: utf-8
import yaml
from datetime import datetime
from sqlalchemy.dialects.mysql import SMALLINT

from app import db, logging
from app.model.validator import ModelValidator
from app.model.enum import StatusEnum, AddressTypeEnum, BooleanEnum
from app.lib.util import Util

LOGGER = logging.getLogger(__name__)


class ModelCustomer(db.Model):
    __tablename__ = 'customers'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'sqlite_autoincrement': True
    }

    id = db.Column(
        SMALLINT(unsigned=True),
        db.Sequence('customer_id_seq'),
        primary_key=True,
        autoincrement=True,
        nullable=False
    )
    name = db.Column(
        db.String(80),
        nullable=False
    )
    type = db.Column(
        SMALLINT(unsigned=True),
        nullable=False
    )
    email = db.Column(
        db.String(50),
        unique=True
    )
    document = db.Column(
        db.String(20)
    )
    status = db.Column(
        db.Enum(StatusEnum, validate_strings=True),
        server_default='enabled',
        default=StatusEnum.enabled,
        index=True
    )
    date_create = db.Column(
        db.DECIMAL(15, 3),
        nullable=False,
        default=lambda : format(datetime.now().timestamp(), '.3f')
    )

    # Create Customer
    def create_customer(self, data):
        v = ModelValidator()
        if not v.validate(data, self.__val_create__()):
            self.errors = v.errors
            return None

        data = v.document

        # if exists
        exists = self.query.filter_by(email=data['email']).first()
        if exists:
            return exists
        
    # Update Customer
    def update_customer(self, data):
        v = ModelValidator()
        if not v.validate(data, self.__val_update__()):
            self.errors = v.errors
            return None

        data = v.document

        customer_id = data.pop('id')
        customer = ModelCustomer.query.filter_by(
            id=customer_id,
            status=StatusEnum.enabled
        ).first()

        if not customer:
            self.errors = {
                'customer': ['customer not found']
            }
            return None

        # pop data partner
        for k in data:
            setattr(customer, k, data[k])

        try:
            db.session.commit()
            return customer
        except Exception as e:
            raise e

     # prepare response dict json
    def get_dict(obj, keys=None, exclude=[]):
        # default keys
        if keys is None:
            keys = [
                'name', 'email', 'type', 'document', 'status'
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
        email:
            maxlength: 50
            type: string
            check_with: email        
        name:
            maxlength: 80
            required: true
            type: string
        
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __val_update__(self):
        schema = '''        
        email:
            maxlength: 50
            type: string
            check_with: email        
        name:
            maxlength: 80
            type: string        
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)
   
    def __repr__(self):
        return "<Customer %r>" % self.name