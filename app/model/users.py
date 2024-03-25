# encoding: utf-8
import yaml
from datetime import datetime
from sqlalchemy.dialects.mysql import INTEGER

from app import db, logging
from app.model.validator import ModelValidator
from app.model.enum import StatusEnum, AddressTypeEnum, BooleanEnum
from app.lib.util import Util

LOGGER = logging.getLogger(__name__)


class ModelUser(db.Model):
    __tablename__ = 'users'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'sqlite_autoincrement': True
    }

    id = db.Column(
        INTEGER(unsigned=True),
        db.Sequence('user_id_seq'),
        primary_key=True,
        autoincrement=True,
        nullable=False
    )
    client_id = db.Column(
        INTEGER(unsigned=True),
        db.ForeignKey('clients.id', onupdate='CASCADE'),
        nullable=False
    )
    user_name = db.Column(
        db.String(40),
        nullable=False
    )
    pwd = db.Column(
        db.String(28)
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
          default=lambda : format(datetime.now().timestamp(), '.3f')
    )

    # RelationShip
    client = db.relationship(
        'ModelClient',
        backref=db.backref('client_user', lazy=True)
    )

    errors = None

    # Create user
    def create_user(self, data):
        v = ModelValidator()
        if not v.validate(data, self.__val_create__()):
            self.errors = v.errors
            return None
            
        data = v.document

        util = Util()        

        # # if exists
        # exists = self.query.filter_by(document=data['document']).first()
        # if exists:
        #     return exists
        
        for k in data:            
            setattr(self, k, data[k])
            # self.uuid = util.gen_uuid()
                        

        try:
            db.session.add(self)
            db.session.commit()
            return self
        except Exception as e:
            raise e
        
    # # Update Client
    # def update_client(self, data):
    #     v = ModelValidator()
    #     if not v.validate(data, self.__val_update__()):
    #         self.errors = v.errors
    #         return None

    #     data = v.document

    #     client_id = data.pop('id')
    #     client = ModelClient.query.filter_by(
    #         id=client_id,
    #         status=StatusEnum.enabled
    #     ).first()

    #     if not client:
    #         self.errors = {
    #             'client': ['client not found']
    #         }
    #         return None

    #     # pop data partner
    #     for k in data:
    #         setattr(client, k, data[k])

    #     try:
    #         db.session.commit()
    #         return client
    #     except Exception as e:
    #         raise e

     # prepare response dict json
    # def get_dict(obj, keys=None, exclude=[]):
    #     # default keys
    #     if keys is None:
    #         keys = [
    #             'name', 'email', 'type', 'document', 'status'
    #         ]

    #     # exclude
    #     for e in exclude:
    #         if e in keys:
    #             keys.pop(e)

    #     util = Util()
    #     return util.get_dict(obj=obj, keys=keys)

    # Validators
    def __val_create__(self):
        schema = '''
        client_id:
            min: 1
            required: true
            type: integer
            coerce: integer 
        user_name:
            maxlength: 40
            required: true
            type: string   
        pwd:
            maxlength: 28
            type: string
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __val_update__(self):
        schema = '''  
        client_id:
            min: 1
            required: true
            type: integer
            coerce: integer      
        user_name:
            maxlength: 40
            required: true
            type: string  
        pwd:
            maxlength: 28
            type: string  
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)
   
    def __repr__(self):
        return "<User %r>" % self.name