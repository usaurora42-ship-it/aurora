# encoding: utf-8
import yaml
from datetime import datetime
from sqlalchemy.dialects.mysql import INTEGER

from app import db, logging
from app.model.validator import ModelValidator
from app.model.enum import StatusEnum

LOGGER = logging.getLogger(__name__)


class ModelOrderItem(db.Model):
    __tablename__ = 'orders_items'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'sqlite_autoincrement': True
    }
    id = db.Column(
        INTEGER(unsigned=True),
        db.Sequence('order_item_id_seq'),
        primary_key=True,
        autoincrement=True,
        nullable=False
    )
    product_id = db.Column(
        INTEGER(unsigned=True),
        db.ForeignKey('products.id', onupdate='CASCADE'),
        nullable=False
    )
    order_id = db.Column(
        INTEGER(unsigned=True),
        db.ForeignKey('orders.id', onupdate='CASCADE'),
        nullable=False
    )
    quantity = db.Column(
        db.Numeric,
        nullable=False,
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
        default=lambda: format(datetime.now().timestamp(), '.3f')
    )

    # RelationShips
    order = db.relationship(
        'ModelOrder',
        backref=db.backref('order_item', lazy=True)
    )
    product = db.relationship(
        'ModelProduct',
        backref=db.backref('order_item_product', lazy=True)
    )

    errors = None

    # Create Order Item
    def create_order_item(self, data):
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

    # Validators
    def __val_create__(self):
        schema = '''
        product_id:
            min: 1
            required: true
            type: integer
            coerce: integer
        order_id:
            min: 1
            required: true
            type: integer
            coerce: integer
        quantity:
            min: 1
            required: true
            type: number
            coerce: float
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __val_update__(self):
        schema = '''
        product_id:
            min: 1
            required: true
            type: integer
            coerce: integer
        order_id:
            min: 1
            required: true
            type: integer
            coerce: integer
        quantity:
            min: 1
            type: number
            coerce: float
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __repr__(self):
        return "<OrderItem %r>" % self.id
