# encoding: utf-8
import yaml
import re
from datetime import datetime
from sqlalchemy.dialects.mysql import INTEGER

from app import db, logging
from app.model.validator import ModelValidator
from app.model.enum import StatusEnum
from app.lib.util import Util

LOGGER = logging.getLogger(__name__)


class ModelProduct(db.Model):
    __tablename__ = 'products'
    __table_args__ = {
        'mysql_engine':    'InnoDB',
        'mysql_charset':   'utf8mb4',
        'mysql_collate':   'utf8mb4_unicode_ci',
        'sqlite_autoincrement': True
    }

    id = db.Column(
        INTEGER(unsigned=True),
        db.Sequence('product_id_seq'),
        primary_key=True,
        autoincrement=True,
        nullable=False
    )
    name = db.Column(
        db.String(120),
        nullable=False
        # unique removido — nomes de produto podem se repetir
    )
    slug = db.Column(
        db.String(160),
        unique=True,
        nullable=True,
        index=True
        # URL amigável: gerado automaticamente a partir do name
        # Ex: "Pulseira Zircônia Rosa" → "pulseira-zirconia-rosa"
    )
    unit_id = db.Column(
        INTEGER(unsigned=True),
        db.ForeignKey('units.id', onupdate='CASCADE'),
        nullable=False
    )
    description = db.Column(
        db.String(255),   # aumentado de 80 para caber descrições reais
        nullable=False
    )
    details = db.Column(
        db.Text,          # descrição longa (material, cuidados, etc.)
        nullable=True
    )
    material = db.Column(
        db.String(120),   # Ex: "Folheado a ouro 18k, zircônia"
        nullable=True
    )
    size = db.Column(
        db.String(80),
        nullable=True
    )
    stock = db.Column(
        INTEGER(unsigned=True),
        nullable=False,
        default=0,
        server_default='0'
    )
    path = db.Column(
        db.String(200)
    )
    value = db.Column(
        db.DECIMAL(15, 2),
        nullable=False
    )
    value_old = db.Column(
        db.DECIMAL(15, 2),
        nullable=True     # preço "de" riscado (opcional)
    )
    date_create = db.Column(
        db.DECIMAL(15, 3),
        nullable=False,
        default=lambda: format(datetime.now().timestamp(), '.3f')
    )
    status = db.Column(
        db.Enum(StatusEnum, validate_strings=True),
        server_default='enabled',
        default=StatusEnum.enabled,
        index=True
    )

    # Relationships
    unit = db.relationship(
        'ModelUnit',
        backref=db.backref('unit_product', lazy=True)
    )

    errors = None

    # ── Gera slug a partir do nome ─────────────────────────────────────────
    @staticmethod
    def generate_slug(name):
        slug = name.lower().strip()
        # Remove acentos básicos
        replacements = {
            'á':'a','à':'a','ã':'a','â':'a','ä':'a',
            'é':'e','è':'e','ê':'e','ë':'e',
            'í':'i','ì':'i','î':'i','ï':'i',
            'ó':'o','ò':'o','õ':'o','ô':'o','ö':'o',
            'ú':'u','ù':'u','û':'u','ü':'u',
            'ç':'c','ñ':'n',
        }
        for k, v in replacements.items():
            slug = slug.replace(k, v)
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'[\s]+', '-', slug)
        slug = re.sub(r'-+', '-', slug).strip('-')
        return slug

    # ── Garante slug único ─────────────────────────────────────────────────
    @staticmethod
    def unique_slug(base_slug):
        slug = base_slug
        counter = 1
        while ModelProduct.query.filter_by(slug=slug).first():
            slug = f'{base_slug}-{counter}'
            counter += 1
        return slug

    # ── Criar produto ──────────────────────────────────────────────────────
    def create_product(self, data):
        v = ModelValidator()
        if not v.validate(data, self.__val_create__()):
            self.errors = v.errors
            return None

        data = v.document

        for k in data:
            setattr(self, k, data[k])

        # Gera slug automaticamente se não foi fornecido
        if not self.slug:
            base = ModelProduct.generate_slug(self.name)
            self.slug = ModelProduct.unique_slug(base)

        try:
            db.session.add(self)
            db.session.commit()
            return self
        except Exception as e:
            raise e

    # ── Atualizar produto ──────────────────────────────────────────────────
    def update_product(self, data):
        v = ModelValidator()
        if not v.validate(data, self.__val_update__()):
            self.errors = v.errors
            return None

        data = v.document
        product_id = data.pop('id')
        product = ModelProduct.query.filter_by(
            id=product_id,
            status=StatusEnum.enabled
        ).first()

        if not product:
            self.errors = {'product': ['Produto não encontrado.']}
            return None

        for k in data:
            setattr(product, k, data[k])

        # Regenera slug se o nome mudou
        if 'name' in data:
            base = ModelProduct.generate_slug(data['name'])
            product.slug = ModelProduct.unique_slug(base)

        try:
            db.session.commit()
            return product
        except Exception as e:
            raise e

    # ── Validators ─────────────────────────────────────────────────────────
    def __val_create__(self):
        schema = '''
        unit_id:
            coerce: integer
            max: 65535
            min: 1
            required: true
            type: integer
        name:
            maxlength: 120
            required: true
            type: string
        description:
            maxlength: 255
            required: true
            type: string
        details:
            type: string
            nullable: true
        material:
            maxlength: 120
            type: string
            nullable: true
        path:
            maxlength: 200
            required: true
            type: string
        size:
            type: string
            maxlength: 80
            nullable: true
        stock:
            type: integer
            coerce: integer
            min: 0
            nullable: true
        value:
            type: number
            coerce: float
            required: true
        value_old:
            type: number
            coerce: float
            nullable: true
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __val_update__(self):
        schema = '''
        id:
            required: true
            type: integer
            coerce: integer
        unit_id:
            coerce: integer
            max: 65535
            min: 1
            type: integer
        name:
            maxlength: 120
            type: string
        description:
            maxlength: 255
            type: string
        details:
            type: string
            nullable: true
        material:
            maxlength: 120
            type: string
            nullable: true
        path:
            maxlength: 200
            type: string
        size:
            type: string
            maxlength: 80
            nullable: true
        stock:
            type: integer
            coerce: integer
            min: 0
            nullable: true
        value:
            type: number
            coerce: float
        value_old:
            type: number
            coerce: float
            nullable: true
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __repr__(self):
        return '<Product %r>' % self.name
