# encoding: utf-8
import yaml
from datetime import datetime
from sqlalchemy.dialects.mysql import INTEGER

from app import db, logging
from app.model.validator import ModelValidator
from app.model.enum import StatusEnum, AddressTypeEnum, BooleanEnum
from app.lib.util import Util

LOGGER = logging.getLogger(__name__)


class ModelCart(db.Model):
    __tablename__ = 'cart'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'sqlite_autoincrement': True
    }

    id = db.Column(
        INTEGER(unsigned=True),
        db.Sequence('cart_id_seq'),
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
        db.DECIMAL(15, 2)
    )  
    quantity = db.Column(
        db.DECIMAL(15, 0)
    ) 
    voucher = db.Column(
        db.DECIMAL(15, 2)
    ) 
    total = db.Column(
        db.DECIMAL(15, 2)
    ) 
    discount = db.Column(
        db.DECIMAL(15, 2)
    ) 
    subtotal = db.Column(
        db.DECIMAL(15, 2)
    ) 
    delivery = db.Column(
        db.DECIMAL(15, 2)
    ) 
    status = db.Column(
        db.Enum(StatusEnum, validate_strings=True),
        default=StatusEnum.enabled,
        server_default='enabled',
        index=True
    )
    payment_code = db.Column(
        db.String(40)
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

    # Create Cart
    def create_cart(self, data):
        v = ModelValidator()
        if not v.validate(data, self.__val_create__()):
            self.errors = v.errors
            return None

        data = v.document     

        util = Util()
   

        for k in data:
            setattr(self, k, data[k])  
            self.uuid = util.gen_uuid()

        try:
            db.session.add(self)
            db.session.commit()
            return self
        except Exception as e:
            raise e 
        

    # Update Cart
    def update_cart(self, data):
        v = ModelValidator()
        if not v.validate(data, self.__val_update__()):
            self.errors = v.errors
            return None

        data = v.document

        cart_id = data.pop('id')
        cart = ModelCart.query.filter_by(
            id=cart_id,
            status=StatusEnum.enabled
        ).first()

        if not cart:
            self.errors = {
                'cart': ['cart not found']
            }
            return None

        # pop data partner
        for k in data:
            setattr(cart, k, data[k])

        try:
            db.session.commit()
            return cart
        except Exception as e:
            raise e
    
    # Validators
    def __val_create__(self):
        schema = '''
        value:
            type: number
            coerce: float
        amount:
            type: number
            coerce: float
        total:
            type: number
            coerce: float       
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __val_update__(self):
        schema = '''        
        value:
            type: number
            coerce: float
        amount:
            type: number
            coerce: float
        total:
            type: number
            coerce: float         
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __repr__(self):
        return "<Cart %r>" % self.name