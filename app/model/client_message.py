# encoding: utf-8
import yaml
from datetime import datetime
from sqlalchemy.dialects.mysql import INTEGER

from app import db, logging
from app.model.validator import ModelValidator
from app.model.enum import StatusEnum, MessageStatusEnum, MessagePriorityEnum, BooleanEnum
from app.lib.util import Util

LOGGER = logging.getLogger(__name__)


class ModelClientMessage(db.Model):
    __tablename__ = 'client_messages'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'sqlite_autoincrement': True
    }

    id = db.Column(
        INTEGER(unsigned=True),
        db.Sequence('client_message_id_seq'),
        primary_key=True,
        autoincrement=True,
        nullable=False
    )
    client_id = db.Column(
        INTEGER(unsigned=True),
        db.ForeignKey('clients.id', onupdate='CASCADE'),
        nullable=False
    )
    message = db.Column(
        db.Text(),
        comment='message'
    )
    priority = db.Column(
        db.Enum(MessagePriorityEnum, validate_strings=True),
        default=MessagePriorityEnum.normal,
        server_default='normal',
        index=True
    )
    state = db.Column(
        db.Enum(MessageStatusEnum, validate_strings=True),
        default=MessageStatusEnum.new,
        server_default='new',
        index=True
    )
    favorite = db.Column(
        db.Enum(BooleanEnum, validate_strings=True),
        default=BooleanEnum.false,
        server_default='false',
        index=True
    )
    is_pushable = db.Column(
        db.Enum(BooleanEnum, validate_strings=True),
        default=BooleanEnum.false,
        server_default='false',
        index=True
    )
    push_sended = db.Column(
        db.Enum(BooleanEnum, validate_strings=True),
        default=BooleanEnum.false,
        server_default='false',
        index=True
    )
    extra_data = db.Column(
        db.JSON
    )
    status = db.Column(
        db.Enum(StatusEnum, validate_strings=True),
        default=StatusEnum.enabled,
        server_default='enabled',
        index=True
    )
    date_create = db.Column(
        db.DECIMAL(15, 3),
        nullable=False,
        default=lambda : format(datetime.now().timestamp(), '.3f')
    )

    client = db.relationship(
        'ModelClient',
        backref=db.backref('client_message', lazy=True)
    )

    errors = None

    # Create Client Message
    def create_client_message(self, data):
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

    # Update Message
    def update_client_message(self, data):
        v = ModelValidator()
        if not v.validate(data, self.__val_update__()):
            self.errors = v.errors
            return None

        data = v.document

        message_id = data.pop('id', None)
        message = ModelClientMessage.query.filter_by(
            id=message_id,
            status=StatusEnum.enabled
        ).first()

        if message is None:
            self.errors = {
                'message': ['message not found']
            }
            return None

        # pop data message
        for k in data:
            setattr(message, k, data[k])

        try:
            db.session.commit()
            return message
        except Exception as e:
            raise e

    # prepare response dict json
    def get_dict(obj, keys=None, exclude=[]):
        util = Util()

        # default keys
        if keys is None:
            keys = [
                'id','message', 'priority', 'state', 'favorite', 'is_pushable',
                'push_sended', 'date_create'
            ]

        # exclude
        for e in exclude:
            if e in keys:
                keys.pop(e)

        return util.get_dict(obj, keys)

    # validators
    def __val_create__(self):
        schema = '''
        client_id:
            coerce: integer
            max: 4294967295
            min: 1
            required: true
            type: integer
        favorite:
            allowed:
            - 'false'
            - 'true'
            coerce: boolean
            type: string
        is_pushable:
            allowed:
            - 'false'
            - 'true'
            coerce: boolean
            type: string
        message:
            type: string
        priority:
            allowed:
            - normal
            - high
            - low
            type: string
        push_sended:
            allowed:
            - 'false'
            - 'true'
            coerce: boolean
            type: string
        state:
            allowed:
            - new
            - shown
            - hidden
            - deleted
            - archived
            type: string
        extra_data:
            check_with: json
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __val_update__(self):
        schema = '''
        favorite:
            allowed:
            - 'false'
            - 'true'
            coerce: boolean
            type: string
        id:
            min: 1
            required: true
            type: integer
        is_pushable:
            allowed:
            - 'false'
            - 'true'
            coerce: boolean
            type: string
        message:
            type: string
        priority:
            allowed:
            - normal
            - high
            - low
            type: string
        push_sended:
            allowed:
            - 'false'
            - 'true'
            coerce: boolean
            type: string
        state:
            allowed:
            - new
            - shown
            - hidden
            - deleted
            - archived
            type: string
        extra_data:
            check_with: json
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __repr__(self):
        return "<ClientMessage %r>" % self.id
