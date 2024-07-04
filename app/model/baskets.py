# encoding: utf-8
import yaml
from datetime import datetime
from sqlalchemy.dialects.mysql import INTEGER

from app import db, logging
from app.model.validator import ModelValidator
from app.model.enum import StatusEnum, AddressTypeEnum, BooleanEnum
from app.lib.util import Util

LOGGER = logging.getLogger(__name__)


class ModelBasket(db.Model):
    __tablename__ = 'baskets'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'sqlite_autoincrement': True
    }

    id = db.Column(
        INTEGER(unsigned=True),
        db.Sequence('basket_id_seq'),
        primary_key=True,
        autoincrement=True,
        nullable=False
    ) 
    product_id = db.Column(
        INTEGER(unsigned=True),
        db.ForeignKey('products.id', onupdate='CASCADE'),
        nullable=False
    )
    category_id = db.Column(
        INTEGER(unsigned=True),
        db.ForeignKey('categories.id', onupdate='CASCADE'),
        nullable=False
    )
    description = db.Column(
        db.String(80),
        nullable=False
    )   
    path = db.Column(
        db.String(200)
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
    status = db.Column(
        db.Enum(StatusEnum, validate_strings=True),
        server_default='enabled',
        default=StatusEnum.enabled,
        index=True
    )

    # relationship
    product = db.relationship(
        'ModelProduct',
        backref=db.backref('basket_product', lazy=True)
    )    

    category = db.relationship(
        'ModelCategory',
        backref=db.backref('category_basket', lazy=True)
    )   
  
    # Create Product    
    def create_basket(self, data):              
        v = ModelValidator()           
        if not v.validate(data, self.__val_create__()):
            self.errors = v.errors  
            return None       

        data = v.document  
        
        util = Util()

        for k in data:
            setattr(self, k, data[k])  

        try:
            db.session.add(self)
            db.session.commit()
            return self
        except Exception as e:
            raise e      
        

    # Update Product
    # def update_product(self, data):
    #     v = ModelValidator()
    #     if not v.validate(data, self.__val_update__()):
    #         self.errors = v.errors
    #         return None

    #     data = v.document

        # product_id = data.pop('id')
        # product= ModelProduct.query.filter_by(
        #     id=product_id,
        #     status=StatusEnum.enabled
        # ).first()

        # if not product:
        #     self.errors = {
        #         'product': ['product not found']
        #     }
        #     return None

        # pop data partner
        # for k in data:
        #     setattr(product, k, data[k])

        # try:
        #     db.session.commit()
        #     return product
        # except Exception as e:
        #     raise e 
    
    # Validators
    def __val_create__(self):
        schema = '''
        product_id:
            coerce: integer
            max: 65535
            min: 1
            required: true
            type: integer
        category_id:
            coerce: integer
            max: 65535
            min: 1
            required: true
            type: integer    
        description:
            maxlength: 80
            required: true
            type: string
        path:
            maxlength: 200
            required: true
            type: string
        value:
            type: number
            coerce: float
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __val_update__(self):
        schema = '''        
        product_id:
            coerce: integer
            max: 65535
            min: 1
            type: integer  
        category_id:
            coerce: integer
            max: 65535
            min: 1
            required: true
            type: integer     
        description:
            maxlength: 80
            type: string
        path:
            maxlength: 200
            required: true
            type: string
        value:
            type: number
            coerce: float
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __repr__(self):
        return "<Basket %r>" % self.name