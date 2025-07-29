# encoding: utf-8
import yaml
from datetime import datetime
from sqlalchemy.dialects.mysql import INTEGER

from app import db, logging
from app.model.validator import ModelValidator

LOGGER = logging.getLogger(__name__)


class ModelCartBasket(db.Model):
    __tablename__ = 'cart_basket'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'sqlite_autoincrement': True
    }

    id = db.Column(
        INTEGER(unsigned=True),
        db.Sequence('cart_basket_id_seq'),
        primary_key=True,
        autoincrement=True,
        nullable=False
    )
    basket_id = db.Column(
        INTEGER(unsigned=True),
        db.ForeignKey('baskets.id', onupdate='CASCADE'),
        nullable=False
    )
    order_id = db.Column(
        INTEGER(unsigned=True),
        db.ForeignKey('orders.id', onupdate='CASCADE'),
        nullable=False
    )
    date_create = db.Column(
        db.DECIMAL(15, 3),
        nullable=False,
        default=lambda : format(datetime.now().timestamp(), '.3f')
    )

    # RelationShip
    cart = db.relationship(
        'ModelOrder',
        backref=db.backref('cart_basket', lazy=True)
    )

    basket = db.relationship(
        'ModelBasket',
        backref=db.backref('basket_cart', lazy=True)
    )

    errors = None

    # Create Cart Basket
    def create_cart_basket(self, data):
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
        cart_id:
            min: 1
            required: true
            type: integer
            coerce: integer
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __repr__(self):
        return "<CartBasket %r>" % self.id
