# encoding: utf-8
from flask import render_template, make_response, abort
from app.blueprints.site import SiteBlueprint
from app.model.category import ModelCategory
from app.model.products import ModelProduct
from app.model.product_category import ModelProductCategory
from app.model.enum import StatusEnum
from app import logging

LOGGER = logging.getLogger(__name__)


@SiteBlueprint.route('/category/<int:category_id>')
def category_products_get(category_id):
    """Lista produtos de uma categoria ou subcategoria."""

    category = ModelCategory.query.filter_by(
        id=category_id,
        status=StatusEnum.enabled
    ).first_or_404()

    # Se for categoria principal, inclui produtos das subcategorias também
    if category.parent_id is None:
        sub_ids = [s.id for s in ModelCategory.query.filter_by(
            parent_id=category.id,
            status=StatusEnum.enabled
        ).all()]
        category_ids = [category.id] + sub_ids
    else:
        category_ids = [category.id]

    products = ModelProduct.query.with_entities(
        ModelProduct.id,
        ModelProduct.name,
        ModelProduct.description,
        ModelProduct.path,
        ModelProduct.value,
        ModelProduct.value_old,
        ModelProduct.slug,
    ).join(
        ModelProductCategory,
        ModelProduct.id == ModelProductCategory.product_id
    ).filter(
        ModelProductCategory.category_id.in_(category_ids),
        ModelProduct.status == StatusEnum.enabled
    ).order_by(ModelProduct.description).all()

    # Subcategorias para o filtro lateral (só se for categoria principal)
    subcategories = []
    if category.parent_id is None:
        subcategories = ModelCategory.query.filter_by(
            parent_id=category.id,
            status=StatusEnum.enabled
        ).order_by(ModelCategory.description).all()

    return make_response(render_template(
        'products/category_products.html',
        category=category,
        products=products,
        subcategories=subcategories,
    ))
