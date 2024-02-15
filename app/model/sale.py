# encoding: utf-8
import yaml
from datetime import datetime
from sqlalchemy.dialects.mysql import INTEGER

from app import db, logging
from app.model.validator import ModelValidator
from app.model.enum import StatusEnum, AddressTypeEnum, BooleanEnum
from app.lib.util import Util

LOGGER = logging.getLogger(__name__)


class ModelSale(db.Model):
    __tablename__ = 'sales'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'sqlite_autoincrement': True
    }

    id = db.Column(
        INTEGER(unsigned=True),
        db.Sequence('sale_id_seq'),
        primary_key=True,
        autoincrement=True,
        nullable=False
    )    
    value = db.Column(
        db.DECIMAL(15, 2),
        nullable=False,
    )  
    voucher = db.Column(
        db.DECIMAL(15, 2),
        nullable=False,
    ) 
    status = db.Column(
        db.Enum(StatusEnum, validate_strings=True),
        default=StatusEnum.enabled,
        server_default='enabled',
        index=True
    )
    payment_code = db.Column(
        db.String(40),
        unique=True,
        nullable=False
    )
    date_create = db.Column(
        db.DECIMAL(15, 3),
        nullable=False,
        default=lambda : format(datetime.now().timestamp(), '.3f')
    )

    # relationship
    client = db.relationship(
        'ModelClient',
        backref=db.backref('client_sale', lazy=True)
    )    

    errors = None

    # Create Sale
    def create_sale(self, data):
        v = ModelValidator()
        if not v.validate(data, self.__val_create__()):
            self.errors = v.errors
            return None

        data = v.document        
        

    # Update Sale
    def update_sale(self, data):
        v = ModelValidator()
        if not v.validate(data, self.__val_update__()):
            self.errors = v.errors
            return None

        data = v.document

        sale_id = data.pop('id')
        sale = ModelSales.query.filter_by(
            id=sale_id,
            status=StatusEnum.enabled
        ).first()

        if not sale:
            self.errors = {
                'sale': ['sale not found']
            }
            return None

        # pop data partner
        for k in data:
            setattr(sale, k, data[k])

        try:
            db.session.commit()
            return sale
        except Exception as e:
            raise e
    
    # Validators
    def __val_create__(self):
        schema = '''
        sale_id:
            coerce: integer
            max: 65535
            min: 1
            required: true
            type: integer        
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __val_update__(self):
        schema = '''        
        sale_id:
            coerce: integer
            max: 65535
            min: 1
            type: integer        
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __repr__(self):
        return "<Sale %r>" % self.name