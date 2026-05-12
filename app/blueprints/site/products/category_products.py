# encoding: utf-8
from flask import render_template, request, redirect
from app.blueprints.site import SiteBlueprint
from app import logging
from app.model.products import ModelProduct
from app.model.enum import StatusEnum
from app.model.product_category import ModelProductCategory
from app.model.category import ModelCategory
from app.model.units import ModelUnit

LOGGER = logging.getLogger(__name__)

# ── Mapeamento slug → nome real da categoria no banco ──────────────────────
# Chave: slug usado na URL  |  Valor: description exato na tabela categories
CATEGORY_SLUG_MAP = {
    'colares':   'Colares',
    'brincos':   'Brincos',
    'aneis':     'Anéis',
    'pulseiras': 'Pulseiras',
    'conjuntos': 'Conjuntos',
    'bolsas':    'Bolsas',
    'presentes': 'Presentes',
}

# ── Helpers ────────────────────────────────────────────────────────────────

def _get_categories():
    return ModelCategory.query.with_entities(
        ModelCategory.id,
        ModelCategory.description
    ).filter_by(status=StatusEnum.enabled).order_by(ModelCategory.description).all()


def _get_units():
    return ModelUnit.query.with_entities(
        ModelUnit.id,
        ModelUnit.description
    ).filter_by(status=StatusEnum.enabled).order_by(ModelUnit.description).all()


def _build_products_query(category_slug=None):
    query = ModelProduct.query.with_entities(
        ModelProduct.id,
        ModelProduct.description,
        ModelProduct.path,
        ModelProduct.value,
    ).filter_by(status=StatusEnum.enabled)

    if category_slug and category_slug in CATEGORY_SLUG_MAP:
        category_name = CATEGORY_SLUG_MAP[category_slug]
        category = ModelCategory.query.filter(
            ModelCategory.description == category_name,
            ModelCategory.status == StatusEnum.enabled
        ).first()

        if category:
            query = query.join(
                ModelProductCategory,
                ModelProduct.id == ModelProductCategory.product_id
            ).filter(
                ModelProductCategory.category_id == category.id
            )

    return query.order_by(ModelProduct.description)


def _render_catalog(category_slug=None):
    categories    = _get_categories()
    units         = _get_units()
    query         = _build_products_query(category_slug)
    page          = request.args.get('page', 1, type=int)
    posts         = query.paginate(page=page, per_page=16, error_out=False)
    category_label = CATEGORY_SLUG_MAP.get(category_slug)
    active_slug   = category_slug or 'todos'

    return render_template(
        '/products/category_products.html',
        categories=categories,
        units=units,
        items=posts.items,
        pagination=posts,
        category_label=category_label,
        active_slug=active_slug,
    )


# ── ROTAS ──────────────────────────────────────────────────────────────────

@SiteBlueprint.route('/products')
@SiteBlueprint.route('/products/todos')
def category_product_all():
    return _render_catalog()

@SiteBlueprint.route('/products/colares')
def category_product_colares():
    return _render_catalog('colares')

@SiteBlueprint.route('/products/brincos')
def category_product_brincos():
    return _render_catalog('brincos')

@SiteBlueprint.route('/products/aneis')
def category_product_aneis():
    return _render_catalog('aneis')

@SiteBlueprint.route('/products/pulseiras')
def category_product_pulseiras():
    return _render_catalog('pulseiras')

@SiteBlueprint.route('/products/conjuntos')
def category_product_conjuntos():
    return _render_catalog('conjuntos')

@SiteBlueprint.route('/products/bolsas')
def category_product_bolsas():
    return _render_catalog('bolsas')

@SiteBlueprint.route('/products/presentes')
def category_product_presentes():
    return _render_catalog('presentes')

# Compatibilidade com URL antiga → redireciona para nova (301)
@SiteBlueprint.route('/products/category_products')
def category_product_legacy():
    cat = request.args.get('cat', '')
    if cat and cat in CATEGORY_SLUG_MAP:
        return redirect(f'/products/{cat}', code=301)
    return redirect('/products', code=301)
