# encoding: utf-8
import yaml
from datetime import datetime
from sqlalchemy.dialects.mysql import INTEGER

from app import db, logging
from app.model.validator import ModelValidator

LOGGER = logging.getLogger(__name__)


class ModelPartnerPhone(db.Model):
    __tablename__ = 'partner_phones'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'sqlite_autoincrement': True
    }

    id = db.Column(
        INTEGER(unsigned=True),
        db.Sequence('client_phone_id_seq'),
        primary_key=True,
        autoincrement=True,
        nullable=False
    )
    partner_id = db.Column(
        INTEGER(unsigned=True),
        db.ForeignKey('partners.id', onupdate='CASCADE'),
        nullable=False
    )
    phone_id = db.Column(
        INTEGER(unsigned=True),
        db.ForeignKey('phones.id', onupdate='CASCADE'),
        nullable=False
    )
    date_create = db.Column(
        db.DECIMAL(15, 3),
        nullable=False,
        default=lambda : format(datetime.now().timestamp(), '.3f')
    )

    # RelationShip
    partner = db.relationship(
        'ModelPartner',
        backref=db.backref('partner_phone', lazy=True)
    )

    phone = db.relationship(
        'ModelPhone',
        backref=db.backref('phone_partner', lazy=True)
    )

    errors = None

    # Create Partner Phone
    def create_partner_phone(self, data):
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
        partner_id:
            min: 1
            required: true
            type: integer
            coerce: integer
        phone_id:
            min: 1
            required: true
            type: integer
            coerce: integer
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __repr__(self):
        return "<PartnerPhone %r>" % self.id
