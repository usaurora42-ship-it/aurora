# encoding: utf-8
import yaml
from datetime import datetime
from sqlalchemy.dialects.mysql import INTEGER

from app import db, logging
from app.model.validator import ModelValidator

LOGGER = logging.getLogger(__name__)


class ModelBasketProduct(db.Model):
    __tablename__ = 'basket_products'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'sqlite_autoincrement': True
    }

    id = db.Column(
        INTEGER(unsigned=True),
        db.Sequence('basket_product_id_seq'),
        primary_key=True,
        autoincrement=True,
        nullable=False
    )
    basket_id = db.Column(
        INTEGER(unsigned=True),
        db.ForeignKey('baskets.id', onupdate='CASCADE'),
        nullable=False
    )
    product_id = db.Column(
        INTEGER(unsigned=True),
        db.ForeignKey('products.id', onupdate='CASCADE'),
        nullable=False
    )
    date_create = db.Column(
        db.DECIMAL(15, 3),
        nullable=False,
        default=lambda : format(datetime.now().timestamp(), '.3f')
    )

    # relationship    
    basket = db.relationship(
        'ModelBasket',
        backref=db.backref('basket_product', lazy=True)
    )
     
    product = db.relationship(
        'ModelProduct',
        backref=db.backref('product_basket', lazy=True)
    )

    errors = None

    # Create Basket Product
    def create_basket_product(self, data):
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

    # validators
    def __val_create__(self):
        schema = '''
        basket_id:
            min: 1
            required: true
            type: integer
            coerce: integer
        product_id:
            min: 1
            required: true
            type: integer
            coerce: integer
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __repr__(self):
        return "<BasketProducts %r>" % self.id
