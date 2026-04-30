# encoding: utf-8
import yaml
from datetime import datetime
from sqlalchemy.dialects.mysql import INTEGER

from app import db, logging
from app.model.validator import ModelValidator
from app.model.enum import StatusEnum
from app.lib.util import Util


LOGGER = logging.getLogger(__name__)


# ── Enums de pagamento ──
# Adicione também estes dois enums no app/model/enum/__init__.py
import enum

class PaymentMethodEnum(enum.Enum):
    pix         = 'pix'
    credit_card = 'credit_card'
    debit_card  = 'debit_card'

class PaymentStatusEnum(enum.Enum):
    pending   = 'pending'    # aguardando pagamento
    approved  = 'approved'   # pagamento aprovado
    rejected  = 'rejected'   # recusado/negado
    cancelled = 'cancelled'  # cancelado pelo cliente


class ModelCheckout(db.Model):
    __tablename__ = 'checkouts'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'sqlite_autoincrement': True
    }

    # ── PRIMARY KEY ──
    id = db.Column(
        INTEGER(unsigned=True),
        db.Sequence('checkout_id_seq'),
        primary_key=True,
        autoincrement=True,
        nullable=False
    )

    # ── UUID (referência externa: webhooks, links de pagamento) ──
    uuid = db.Column(
        db.String(36),
        unique=True,
        nullable=False
    )

    # ── FOREIGN KEYS (tabelas existentes do projeto) ──
    order_id = db.Column(
        INTEGER(unsigned=True),
        db.ForeignKey('orders.id', onupdate='CASCADE'),
        nullable=False,
        index=True
    )
    client_id = db.Column(
        INTEGER(unsigned=True),
        db.ForeignKey('clients.id', onupdate='CASCADE'),
        nullable=False,
        index=True
    )
    address_id = db.Column(
        INTEGER(unsigned=True),
        db.ForeignKey('addresses.id', onupdate='CASCADE'),
        nullable=True   # endereço criado junto com o checkout
    )

    # ── CONTATO ──
    email = db.Column(
        db.String(150),
        nullable=False
    )

    # ── ENDEREÇO DE ENTREGA ──
    zip_code      = db.Column(db.String(9),   nullable=False)
    street        = db.Column(db.String(200),  nullable=False)
    street_number = db.Column(db.String(20),   nullable=False)
    complement    = db.Column(db.String(100),  nullable=True)
    district      = db.Column(db.String(100),  nullable=False)
    city          = db.Column(db.String(100),  nullable=False)
    state         = db.Column(db.String(2),    nullable=False)

    # ── ENTREGA ──
    notes = db.Column(
        db.String(500),
        nullable=True
    )

    # ── PAGAMENTO ──
    payment_method = db.Column(
        db.Enum(PaymentMethodEnum, validate_strings=True),
        nullable=False
    )
    payment_status = db.Column(
        db.Enum(PaymentStatusEnum, validate_strings=True),
        server_default='pending',
        default=PaymentStatusEnum.pending,
        index=True
    )
    payment_external_id = db.Column(
        db.String(100),  # ID retornado pelo Mercado Pago
        nullable=True
    )

    # ── VALOR TOTAL (snapshot no momento do pedido) ──
    total_value = db.Column(
        db.DECIMAL(15, 2),
        nullable=False
    )

    # ── CONTROLE PADRÃO DO PROJETO ──
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

    # ── RELATIONSHIPS ──
    order = db.relationship(
        'ModelOrder',
        backref=db.backref('checkout', lazy=True)
    )
    client = db.relationship(
        'ModelClient',
        backref=db.backref('client_checkout', lazy=True)
    )
    address = db.relationship(
        'ModelAddress',
        backref=db.backref('address_checkout', lazy=True)
    )

    errors = None

    # ── CREATE ──
    def create_checkout(self, data):
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

    # ── UPDATE PAYMENT STATUS (chamado pelo webhook do gateway) ──
    def update_payment_status(self, new_status, external_id=None):
        try:
            self.payment_status = new_status
            if external_id:
                self.payment_external_id = external_id
            db.session.commit()
            return self
        except Exception as e:
            raise e

    # ── VALIDATORS ──
    def __val_create__(self):
        schema = '''
        order_id:
            min: 1
            required: true
            type: integer
            coerce: integer
        client_id:
            min: 1
            required: true
            type: integer
            coerce: integer
        address_id:
            min: 1
            required: false
            type: integer
            coerce: integer
        email:
            maxlength: 150
            required: true
            type: string
        zip_code:
            maxlength: 9
            required: true
            type: string
        street:
            maxlength: 200
            required: true
            type: string
        street_number:
            maxlength: 20
            required: true
            type: string
        complement:
            maxlength: 100
            required: false
            type: string
        district:
            maxlength: 100
            required: true
            type: string
        city:
            maxlength: 100
            required: true
            type: string
        state:
            maxlength: 2
            required: true
            type: string
        notes:
            maxlength: 500
            required: false
            type: string
        payment_method:
            required: true
            type: string
            allowed:
                - pix
                - credit_card
                - debit_card
        total_value:
            required: true
            type: number
            coerce: float
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __val_update__(self):
        schema = '''
        payment_status:
            required: true
            type: string
            allowed:
                - pending
                - approved
                - rejected
                - cancelled
        payment_external_id:
            maxlength: 100
            required: false
            type: string
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __repr__(self):
        return "<Checkout %r>" % self.id