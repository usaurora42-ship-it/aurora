# encoding: utf-8
import yaml
from datetime import datetime
from sqlalchemy.dialects.mysql import INTEGER

from app import db, logging
from app.model.validator import ModelValidator

LOGGER = logging.getLogger(__name__)


class ModelClientAddress(db.Model):
    __tablename__ = 'client_addresses'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'sqlite_autoincrement': True
    }

    id = db.Column(
        INTEGER(unsigned=True),
        db.Sequence('client_address_id_seq'),
        primary_key=True,
        autoincrement=True,
        nullable=False
    )
    client_id = db.Column(
        INTEGER(unsigned=True),
        db.ForeignKey('clients.id', onupdate='CASCADE'),
        nullable=False
    )
    address_id = db.Column(
        INTEGER(unsigned=True),
        db.ForeignKey('addresses.id', onupdate='CASCADE'),
        nullable=False
    )
    date_create = db.Column(
        db.DECIMAL(15, 3),
        nullable=False,
        default=lambda : format(datetime.now().timestamp(), '.3f')
    )

    client = db.relationship(
        'ModelClient',
        backref=db.backref('client_address', lazy=True)
    )

    address = db.relationship(
        'ModelAddress',
        backref=db.backref('address_client', lazy=True)
    )

    errors = None

    # Create Client Address
    def create_client_address(self, data):
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
        address_id:
            min: 1
            required: true
            type: integer
            coerce: integer
        client_id:
            min: 1
            required: true
            type: integer
            coerce: integer
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __repr__(self):
        return "<ClientAddress %r>" % self.id
