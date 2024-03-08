# encoding: utf-8
import yaml
from datetime import datetime
from sqlalchemy.dialects.mysql import INTEGER

from app import db, logging
from app.model.validator import ModelValidator
from app.model.enum import StatusEnum, MessageStatusEnum, MessagePriorityEnum, BooleanEnum
from app.lib.util import Util

LOGGER = logging.getLogger(__name__)


class ModelClientGifted(db.Model):
    __tablename__ = 'client_gifted'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'sqlite_autoincrement': True
    }

    id = db.Column(
        INTEGER(unsigned=True),
        db.Sequence('client_gifted_id_seq'),
        primary_key=True,
        autoincrement=True,
        nullable=False
    )
    client_id = db.Column(
        INTEGER(unsigned=True),
        db.ForeignKey('clients.id', onupdate='CASCADE'),
        nullable=False
    )
    gifted_name = db.Column(
        db.String(80),
        nullable=False
    )
    gifted_ocasion = db.Column(
        db.String(80),
        nullable=False
    )
    signature_card = db.Column(
        db.String(80),
        nullable=False
    )
    gifted_message = db.Column(
        db.Text(),
        comment='message'
    ) 
    code_country = db.Column(
        db.String(4),
        nullable=False,
        server_default='55'
    )
    code_area = db.Column(
        db.String(4),
        nullable=False
    )
    number = db.Column(
        db.String(15),
        nullable=False
    )
    status = db.Column(
         db.Enum(StatusEnum, validate_strings=True),
         server_default='enabled',
         default=StatusEnum.enabled,
         index=True
     )

    # RelationShip
    client = db.relationship(
        'ModelClient',
        backref=db.backref('client_gifted', lazy=True)
    )

    errors = None

    # Create Gifted
    def create_client_gifted(self, data):
        v = ModelValidator()
        if not v.validate(data, self.__val_create__()):
            print("giftedwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww")
            print(v.errors)
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

    # Update Gifted
    # def update_client_message(self, data):
    #     v = ModelValidator()
    #     if not v.validate(data, self.__val_update__()):
    #         self.errors = v.errors
    #         return None

    #     data = v.document

    #     gifted_id = data.pop('id', None)
    #     gifted = ModelClientGifted.query.filter_by(
    #         id=gifted_id,
    #         status=StatusEnum.enabled
    #     ).first()

    #     if gifted is None:
    #         self.errors = {
    #             'gifted': ['gifted not found']
    #         }
    #         return None

    #     # pop data gifted
    #     for k in data:
    #         setattr(gifted, k, data[k])
    #         print("gifted_data")
    #         print(data[k])

    #     try:
    #         db.session.commit()
    #         return gifted
    #     except Exception as e:
    #         raise e

    # # prepare response dict json
    # def get_dict(obj, keys=None, exclude=[]):
    #     util = Util()

    #     """ # default keys
    #     if keys is None:
    #         keys = [
    #             'id','message', 'priority', 'state', 'favorite', 'is_pushable',
    #             'push_sended', 'date_create'
    #         ] """

    #     # exclude
    #     for e in exclude:
    #         if e in keys:
    #             keys.pop(e)

    #     return util.get_dict(obj, keys)

    # validators
    def __val_create__(self):
        schema = '''  
        client_id:
            min: 1
            required: true
            type: integer
            coerce: integer     
        gifted_name:
            type: string   
        gifted_ocasion:
            type: string 
        signature_card:
            type: string       
        gifted_message:
            type: string   
        code_area:
            maxlength: 4
            required: true
            type: string
            coerce: str
        code_country:
            maxlength: 4
            required: true
            type: string
            coerce: str
        number:
            maxlength: 15
            required: true
            type: string
            coerce: str 
 
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    # def __val_update__(self):
    #     schema = '''
    #     client_id:
    #         min: 1
    #         required: true
    #         type: integer
    #         coerce: integer
    #     gifted_name:
    #         type: string   
    #     gifted_ocasion:
    #         type: string 
    #     signature_card:
    #         type: string       
    #     gifted_message:
    #         type: string 
    #     code_area:
    #         maxlength: 4
    #         required: true
    #         type: string
    #         coerce: str
    #     code_country:
    #         maxlength: 4
    #         required: true
    #         type: string
    #         coerce: str
    #     number:
    #         maxlength: 15
    #         required: true
    #         type: string
    #         coerce: str  
    #     '''
    #     return yaml.load(schema, Loader=yaml.FullLoader)

    def __repr__(self):
        return "<ClientGifted %r>" % self.id
