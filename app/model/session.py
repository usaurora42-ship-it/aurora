# encoding: utf-8
import yaml
from datetime import datetime
from sqlalchemy.dialects.mysql import INTEGER

from app import db, logging
from app.model.validator import ModelValidator
from app.model.enum import StatusEnum, AddressTypeEnum, BooleanEnum
from app.lib.util import Util

LOGGER = logging.getLogger(__name__)


class ModelSession(db.Model):
    __tablename__ = 'sessions'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'sqlite_autoincrement': True
    }

    id = db.Column(
        INTEGER(unsigned=True),
        db.Sequence('session_id_seq'),
        primary_key=True,
        autoincrement=True,
        nullable=False
    )
    # uuid = db.Column(
    #       db.String(36),
    #       unique=True,
    #       nullable=False
    # )  
    user_id = db.Column(
        INTEGER(unsigned=True),
        db.ForeignKey('clients.id', onupdate='CASCADE'),
        nullable=False
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

    # Create Session
    def create_session(self, data):
        v = ModelValidator()
        if not v.validate(data, self.__val_create__()):
            self.errors = v.errors
            return None
            
        data = v.document

        util = Util()

        
        for k in data:            
            setattr(self, k, data[k])
            self.uuid = util.gen_uuid()
            

        try:
            db.session.add(self)
            db.session.commit()
            return self
        except Exception as e:
            raise e
        
    
    # Validators
    def __val_create__(self):
        schema = '''
        user_id:
            min: 1
            required: true
            type: integer
            coerce: integer   
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __val_update__(self):
        schema = '''        
        user_id:
            min: 1
            required: true
            type: integer
            coerce: integer
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)
   
    def __repr__(self):
        return "<Session %r>" % self.name