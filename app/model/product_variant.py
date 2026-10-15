# encoding: utf-8
import yaml

from sqlalchemy.dialects.mysql import INTEGER

from app import db, logging
from app.model.validator import ModelValidator

LOGGER = logging.getLogger(__name__)


class ModelProductVariant(db.Model):
    """Uma variação (tamanho) de um produto, com estoque próprio.

    Ex.: produto "Anel Geométrico Zircônia" -> variações 16, 17, 19, 24.
    """
    __tablename__ = 'product_variants'
    __table_args__ = (
        db.UniqueConstraint('product_id', 'size', name='uq_variant_product_size'),
        {
            'mysql_engine':    'InnoDB',
            'mysql_charset':   'utf8mb4',
            'mysql_collate':   'utf8mb4_unicode_ci',
            'sqlite_autoincrement': True
        }
    )

    id = db.Column(
        INTEGER(unsigned=True),
        db.Sequence('product_variant_id_seq'),
        primary_key=True,
        autoincrement=True,
        nullable=False
    )
    product_id = db.Column(
        INTEGER(unsigned=True),
        db.ForeignKey('products.id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    size = db.Column(
        db.String(20),      # "16", "17", "P", "M", "45cm"...
        nullable=False
    )
    size_order = db.Column(
        db.Integer,         # só para ordenar (16, 17, 19, 24)
        nullable=False,
        default=0,
        server_default='0'
    )
    stock = db.Column(
        INTEGER(unsigned=True),
        nullable=False,
        default=0,
        server_default='0'
    )
    value = db.Column(
        db.DECIMAL(15, 2),
        nullable=True       # opcional: sobrescreve o preço do produto
    )

    # Relationships (backref cria ModelProduct.variants, sem editar o model)
    product = db.relationship(
        'ModelProduct',
        backref=db.backref(
            'variants',
            lazy=True,
            cascade='all, delete-orphan',
            order_by='ModelProductVariant.size_order, ModelProductVariant.size'
        )
    )

    errors = None

    # ── SKU calculado: "<id do produto>-<tamanho>" ─────────────────────────
    @property
    def sku(self):
        return f'{self.product_id}-{self.size}'

    @property
    def price(self):
        return self.value if self.value is not None else self.product.value

    @property
    def available(self):
        return self.stock > 0

    @property
    def last_piece(self):
        return self.stock == 1

    @staticmethod
    def _order_of(size):
        try:
            return int(str(size).strip())
        except ValueError:
            return 0

    # ── Cria/atualiza as variações de um produto de uma vez ───────────────
    # items: [{'size': '16', 'stock': 3}, {'size': '17', 'stock': 1}, ...]
    # Tamanhos que não vierem na lista são removidos.
    @staticmethod
    def sync_variants(product_id, items):
        v = ModelValidator()
        clean = []
        seen = set()
        for item in items:
            if not v.validate(item, ModelProductVariant.__val_item__()):
                errors = v.errors
                return None, errors
            doc = v.document
            size = doc['size'].strip()
            if not size or size in seen:
                continue
            seen.add(size)
            clean.append({
                'size': size,
                'stock': doc.get('stock') or 0,
                'value': doc.get('value'),
            })

        existing = {
            x.size: x for x in
            ModelProductVariant.query.filter_by(product_id=product_id).all()
        }

        try:
            for item in clean:
                row = existing.pop(item['size'], None)
                if row is None:
                    row = ModelProductVariant(
                        product_id=product_id,
                        size=item['size']
                    )
                    db.session.add(row)
                row.stock = item['stock']
                row.value = item['value']
                row.size_order = ModelProductVariant._order_of(item['size'])

            # remove os que saíram da lista
            # (se houver pedidos ligados a variações, troque por soft delete)
            for row in existing.values():
                db.session.delete(row)

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

        return ModelProductVariant.query.filter_by(product_id=product_id).all(), None

    # ── Baixa de estoque atômica (evita vender a mesma última peça 2x) ────
    @staticmethod
    def decrement_stock(variant_id, qty=1):
        rows = ModelProductVariant.query.filter(
            ModelProductVariant.id == variant_id,
            ModelProductVariant.stock >= qty
        ).update(
            {ModelProductVariant.stock: ModelProductVariant.stock - qty},
            synchronize_session=False
        )
        db.session.commit()
        return rows == 1   # False = sem estoque suficiente

    # ── Validator ──────────────────────────────────────────────────────────
    @staticmethod
    def __val_item__():
        schema = '''
        size:
            maxlength: 20
            required: true
            type: string
        stock:
            type: integer
            coerce: integer
            min: 0
            nullable: true
        value:
            type: number
            coerce: float
            nullable: true
        '''
        return yaml.load(schema, Loader=yaml.FullLoader)

    def __repr__(self):
        return '<ProductVariant %r %r>' % (self.product_id, self.size)