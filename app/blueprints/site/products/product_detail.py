# encoding: utf-8
from flask import render_template, make_response, abort
from app.blueprints.site import SiteBlueprint
from app.model.products import ModelProduct
from app.model.product_category import ModelProductCategory
from app.model.category import ModelCategory
from app.model.enum import StatusEnum
from app import logging

LOGGER = logging.getLogger(__name__)


@SiteBlueprint.route('/products/<slug_or_id>')
def product_detail(slug_or_id):
    """Página de detalhe do produto — aceita slug ou ID numérico."""

    # Tenta buscar por ID numérico primeiro, depois por slug
    if slug_or_id.isdigit():
        product = ModelProduct.query.filter_by(
            id=int(slug_or_id),
            status=StatusEnum.enabled
        ).first()
    else:
        product = ModelProduct.query.filter_by(
            slug=slug_or_id,
            status=StatusEnum.enabled
        ).first()

    if product is None:
        abort(404)

    # Busca categoria do produto
    category = ModelCategory.query.join(
        ModelProductCategory,
        ModelCategory.id == ModelProductCategory.category_id
    ).filter(
        ModelProductCategory.product_id == product.id,
        ModelCategory.status == StatusEnum.enabled
    ).first()

    # Busca produtos relacionados (mesma categoria, exceto o atual)
    related = []
    if category:
        related = ModelProduct.query.with_entities(
            ModelProduct.id,
            ModelProduct.name,
            ModelProduct.description,
            ModelProduct.path,
            ModelProduct.value,
            ModelProduct.slug,
        ).join(
            ModelProductCategory,
            ModelProduct.id == ModelProductCategory.product_id
        ).filter(
            ModelProductCategory.category_id == category.id,
            ModelProduct.id != product.id,
            ModelProduct.status == StatusEnum.enabled
        ).limit(4).all()

    return make_response(render_template(
        'products/product_detail.html',
        product=product,
        category=category,
        related=related,
    ))
