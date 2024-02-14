# encoding: utf-8
import yaml
from datetime import datetime
from sqlalchemy.dialects.mysql import INTEGER

from app import db, logging
from app.model.validator import ModelValidator
from app.model.enum import StatusEnum, NotificationDeviceEnum
from app.lib.util import Util

class ModelCustomerMessages(db.Model):
    __tablename__ = 'customer_messages'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'sqlite_autoincrement': True
    }

    id = db.Column(
        INTEGER(unsigned=True),
        db.Sequence('customer_message_id_seq'),
        primary_key=True,
        autoincrement=True,
        nullable=False
    )
    customer_id = db.Column(
        INTEGER(unsigned=True),
        db.ForeignKey('customers.id', onupdate='CASCADE'),
        nullable=False
    )   
   
    message = db.Column(
        db.Text,
        nullable=False
    )
    
    date_create = db.Column(
        db.DECIMAL(15, 3),
        nullable=False,
        default=lambda : format(datetime.now().timestamp(), '.3f')
    )

    customer = db.relationship(
        'ModelCustomer',
        backref=db.backref('customer_message', lazy=True)
    )

    errors = None
    created = False

    # Create Customer Message
    def create_customer_message(self, data):
        v = ModelValidator()
        if not v.validate(data, self.__val_create__()):
            self.errors = v.errors
            return None

        data = v.document
       
        db.session.commit()

    def __repr__(self):
        return "<CustomerMessages %r>" % self.id
