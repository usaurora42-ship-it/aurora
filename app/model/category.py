# encoding: utf-8
import yaml
from sqlalchemy.dialects.mysql import INTEGER
from datetime import datetime

from app import db, logging
from app.model.validator import ModelValidator
from app.model.enum import StatusEnum
from app.lib.util import Util

LOGGER = logging.getLogger(__name__)


class ModelCategory(db.Model):
    __tablename__ = 'categories'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'sqlite_autoincrement': True,
        'extend_existing': True   # ← adicione esta linha
    }

    id = db.Column(
        INTEGER(unsigned=True),
        db.Sequence('category_id_seq'),
        primary_key=True,
        autoincrement=True,
        nullable=False
    )
    parent_id = db.Column(
        INTEGER(unsigned=True),
        db.ForeignKey('categories.id', onupdate='CASCADE', ondelete='SET NULL'),
        nullable=True,   # NULL = categoria principal; preenchido = subcategoria
    )
    description = db.Column(
        db.String(80),   # aumentado de 40 para suportar nomes mais descritivos
        nullable=False
    )
    status = db.Column(
        db.Enum(StatusEnum, validate_strings=True),
        server_default='enabled',
        default=StatusEnum.enabled,
        index=True
    )

    # Subcategorias filhas desta categoria
    subcategories = db.relationship(
        'ModelCategory',
        backref=db.backref('parent', remote_side='ModelCategory.id'),
        lazy='dynamic',
        primaryjoin='ModelCategory.parent_id == ModelCategory.id'
    )

    errors = None

    # Criar categoria (principal ou subcategoria)
    def create_category(self, data):
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

    # Buscar categorias principais com subcategorias (para o menu dropdown)
    @staticmethod
    def get_menu():
        parents = ModelCategory.query.filter_by(
            parent_id=None,
            status=StatusEnum.enabled
        ).order_by(ModelCategory.description).all()

        result = []
        for cat in parents:
            subs = ModelCategory.query.filter_by(
                parent_id=cat.id,
                status=StatusEnum.enabled
            ).order_by(ModelCategory.description).all()
            result.append({'category': cat, 'subcategories': subs})

        return result

    # Prepara dict para JSON
    def get_dict(obj, keys=None, exclude=[]):
        util = Util()
        if keys is None:
            keys = ['id', 'description', 'parent_id']
        for e in exclude:
            if e in keys:
                keys.remove(e)
        return util.get_dict(obj=obj, keys=keys)

    # Validators
    def __val_create__(self):
        schema = '''
        description:
            type: string
            maxlength: 80
            required: true
        parent_id:
            type: integer
            coerce: integer
            min: 1
            nullable: true
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __repr__(self):
        return "<Category %r>" % self.description
