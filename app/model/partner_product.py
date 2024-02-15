# encoding: utf-8
import yaml
from datetime import datetime
from sqlalchemy.dialects.mysql import INTEGER

from app import db, logging
from app.model.validator import ModelValidator


LOGGER = logging.getLogger(__name__)


class ModelPartnerProduct(db.Model):
    __tablename__ = 'partner_products'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'sqlite_autoincrement': True
    }

    id = db.Column(
        INTEGER(unsigned=True),
        db.Sequence('partner_products_id_seq'),
        primary_key=True,
        autoincrement=True,
        nullable=False
    )
    partner_id = db.Column(
        INTEGER(unsigned=True),
        db.ForeignKey('partners.id', onupdate='CASCADE'),
        nullable=False
    )
    products_id = db.Column(
        INTEGER(unsigned=True),
        db.ForeignKey('products.id', onupdate='CASCADE'),
        nullable=False
    )
    date_create = db.Column(
        db.DECIMAL(15, 3),
        nullable=False,
        default=lambda : format(datetime.now().timestamp(), '.3f')
    )

    partner = db.relationship(
        'ModelPartner',
        backref=db.backref('partner_products', lazy=True)
    )

    address = db.relationship(
        'ModelProduct',
        backref=db.backref('product_partners', lazy=True)
    )

    errors = None

    # Create Partner Product
    def create_partner_product(self, data):
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
        products_id:
            min: 1
            required: true
            type: integer
            coerce: integer
        partner_id:
            min: 1
            required: true
            type: integer
            coerce: integer
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __repr__(self):
        return "<PartnerProduct %r>" % self.id
