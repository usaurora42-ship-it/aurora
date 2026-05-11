# encoding: utf-8
import yaml
from datetime import datetime
from sqlalchemy.dialects.mysql import INTEGER

from app import db, logging
from app.model.validator import ModelValidator
from app.model.enum import StatusEnum, BooleanEnum
from app.lib.util import Util

LOGGER = logging.getLogger(__name__)


class ModelClient(db.Model):
    __tablename__ = 'clients'
    __table_args__ = {
        'mysql_engine':    'InnoDB',
        'mysql_charset':   'utf8mb4',
        'mysql_collate':   'utf8mb4_unicode_ci',
        'sqlite_autoincrement': True
    }

    id = db.Column(
        INTEGER(unsigned=True),
        db.Sequence('client_id_seq'),
        primary_key=True,
        autoincrement=True,
        nullable=False
    )
    uuid = db.Column(
        db.String(36),
        unique=True,
        nullable=False
    )
    name = db.Column(
        db.String(80),
        nullable=False
    )
    type = db.Column(
        db.String(2)
    )
    email = db.Column(
        db.String(150),
        unique=True
    )
    document = db.Column(
        db.String(20),
        nullable=True          # ← era implicitamente exigido na validação; agora explicitamente opcional
    )

    # Campos novos para o fluxo de 2 etapas
    # Execute a migration abaixo se a tabela já existir:
    #   ALTER TABLE clients
    #     ADD COLUMN birth_date DATE NULL AFTER document,
    #     ADD COLUMN gender     VARCHAR(1) NULL AFTER birth_date,
    #     ADD COLUMN newsletter TINYINT(1) NOT NULL DEFAULT 0 AFTER gender;
    birth_date = db.Column(
        db.Date,
        nullable=True
    )
    gender = db.Column(
        db.String(1),          # 'F', 'M', 'O'
        nullable=True
    )
    newsletter = db.Column(
        db.SmallInteger,
        nullable=False,
        default=0,
        server_default='0'
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

    # ──────────────────────────────────────────
    #  Criar cliente
    # ──────────────────────────────────────────
    def create_client(self, data):
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

    # ──────────────────────────────────────────
    #  Atualizar cliente
    # ──────────────────────────────────────────
    def update_client(self, data):
        v = ModelValidator()
        if not v.validate(data, self.__val_update__()):
            self.errors = v.errors
            return None

        data = v.document
        client_id = data.pop('id')
        client = ModelClient.query.filter_by(
            id=client_id,
            status=StatusEnum.enabled
        ).first()

        if not client:
            self.errors = {'client': ['Cliente não encontrado.']}
            return None

        for k in data:
            setattr(client, k, data[k])

        try:
            db.session.commit()
            return client
        except Exception as e:
            raise e

    # ──────────────────────────────────────────
    #  Validators
    # ──────────────────────────────────────────
    def __val_create__(self):
        # document, birth_date, gender e newsletter são todos opcionais
        schema = '''
        name:
            type: string
            required: true
            maxlength: 80
        email:
            maxlength: 150
        type:
            maxlength: 2
        document:
            maxlength: 20
        birth_date:
            nullable: true
        gender:
            maxlength: 1
            nullable: true
        newsletter:
            nullable: true
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __val_update__(self):
        schema = '''
        id:
            required: true
        name:
            type: string
            maxlength: 80
        email:
            maxlength: 150
        type:
            maxlength: 2
        document:
            maxlength: 20
        birth_date:
            nullable: true
        gender:
            maxlength: 1
            nullable: true
        newsletter:
            nullable: true
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __repr__(self):
        return '<Client %r>' % self.name
