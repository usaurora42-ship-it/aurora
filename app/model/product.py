# encoding: utf-8
import yaml
from datetime import datetime
from sqlalchemy.dialects.mysql import SMALLINT

from app import db, logging
from app.model.validator import ModelValidator
from app.model.enum import StatusEnum, AddressTypeEnum, BooleanEnum
from app.lib.util import Util

LOGGER = logging.getLogger(__name__)


class ModelProduct(db.Model):
    __tablename__ = 'products'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'sqlite_autoincrement': True
    }

    id = db.Column(
        SMALLINT(unsigned=True),
        db.Sequence('product_id_seq'),
        primary_key=True,
        autoincrement=True,
        nullable=False
    )    
    unit_id = db.Column(
        SMALLINT(unsigned=True),
        db.ForeignKey('units.id', onupdate='CASCADE'),
        nullable=False
    )
    description = db.Column(
        db.String(80),
        nullable=False
    )
    value = db.Column(
        db.DECIMAL(15, 2),
        nullable=False,
    )    
    date_create = db.Column(
        db.DECIMAL(15, 3),
        nullable=False,
        default=lambda : format(datetime.now().timestamp(), '.3f')
    )

    # relationship
    unit = db.relationship(
        'ModelUnit',
        backref=db.backref('unit_product', lazy=True)
    )    

    errors = None

    # Create Product
    def create_product(self, data):
        v = ModelValidator()
        if not v.validate(data, self.__val_create__()):
            self.errors = v.errors
            return None

        data = v.document        
        

    # Update Product
    def update_product(self, data):
        v = ModelValidator()
        if not v.validate(data, self.__val_update__()):
            self.errors = v.errors
            return None

        data = v.document

        product_id = data.pop('id')
        product= ModelProduct.query.filter_by(
            id=product_id,
            status=StatusEnum.enabled
        ).first()

        if not product:
            self.errors = {
                'product': ['product not found']
            }
            return None

        # pop data partner
        for k in data:
            setattr(product, k, data[k])

        try:
            db.session.commit()
            return product
        except Exception as e:
            raise e
    
    # Validators
    def __val_create__(self):
        schema = '''
        unit_id:
            coerce: integer
            max: 65535
            min: 1
            required: true
            type: integer        
        description:
            maxlength: 80
            required: true
            type: string
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __val_update__(self):
        schema = '''        
        unit_id:
            coerce: integer
            max: 65535
            min: 1
            type: integer        
        description:
            maxlength: 80
            type: string
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __repr__(self):
        return "<Product %r>" % self.name