# encoding: utf-8
import yaml
from datetime import datetime
from sqlalchemy.dialects.mysql import INTEGER

from app import db, logging
from app.model.validator import ModelValidator
from app.model.enum import StatusEnum, AddressTypeEnum, BooleanEnum
from app.lib.util import Util

LOGGER = logging.getLogger(__name__)


class ModelCheckout(db.Model):
    __tablename__ = 'checkout'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'sqlite_autoincrement': True
    }

    id = db.Column(
        INTEGER(unsigned=True),
        db.Sequence('checkout_id_seq'),
        primary_key=True,
        autoincrement=True,
        nullable=False
    )  
    uuid = db.Column(
        db.String(36),
        unique=True,
        nullable=False
    )  
    value = db.Column(
        db.DECIMAL(15, 2),
        nullable=False
    )  
    amount = db.Column(
        db.DECIMAL(15, 0),
        nullable=False
    ) 
    voucher = db.Column(
        db.DECIMAL(15, 2)
    ) 
    total = db.Column(
        db.DECIMAL(15, 2),
        nullable=False
    ) 
    discount = db.Column(
        db.DECIMAL(15, 2)
    ) 
    subtotal = db.Column(
        db.DECIMAL(15, 2),
        nullable=False
    ) 
    delivery = db.Column(
        db.DECIMAL(15, 2),
        nullable=False
    ) 
    status = db.Column(
        db.Enum(StatusEnum, validate_strings=True),
        default=StatusEnum.enabled,
        server_default='enabled',
        index=True
    )
    payment_code = db.Column(
        db.String(40),
        unique=True
    )
    date_delivery = db.Column(
        db.DECIMAL(15, 3),
        nullable=False,
        default=lambda : format(datetime.now().timestamp(), '.3f')
    )
    time_slot = db.Column(
        db.String(20),
        unique=True,
        nullable=False,
        default=lambda : format(datetime.now().timestamp(), '.3f')
    )
    date_create = db.Column(
        db.DECIMAL(15, 3),
        nullable=False,
        default=lambda : format(datetime.now().timestamp(), '.3f')
    ) 

    errors = None

    # Create Checkout
    def create_checkout(self, data):
        v = ModelValidator()
        if not v.validate(data, self.__val_create__()):
            self.errors = v.errors
            return None

        data = v.document        
        

    # Update Checkout
    def update_checkout(self, data):
        v = ModelValidator()
        if not v.validate(data, self.__val_update__()):
            self.errors = v.errors
            return None

        data = v.document

        checkout_id = data.pop('id')
        checkout = ModelCheckout.query.filter_by(
            id=checkout_id,
            status=StatusEnum.enabled
        ).first()

        if not checkout:
            self.errors = {
                'checkout': ['checkout not found']
            }
            return None

        # pop data partner
        for k in data:
            setattr(checkout, k, data[k])

        try:
            db.session.commit()
            return checkout
        except Exception as e:
            raise e
    
    # Validators
    def __val_create__(self):
        schema = '''
        checkout_id:
            coerce: integer
            max: 65535
            min: 1
            required: true
            type: integer        
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __val_update__(self):
        schema = '''        
        checkout_id:
            coerce: integer
            max: 65535
            min: 1
            type: integer        
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __repr__(self):
        return "<Checkout %r>" % self.name