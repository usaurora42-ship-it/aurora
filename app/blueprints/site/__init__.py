# encoding: utf-8
from flask import Blueprint

SiteBlueprint = Blueprint('site_bp', 'site', url_prefix='')

from app.blueprints.site import home
from app.blueprints.site.client import signup, login
from app.blueprints.site.products import products
from app.blueprints.site.products import category_products
from app.blueprints.site.hello import hello
from app.blueprints.site.cart import cart
from app.blueprints.site.cart import checkout
from app.blueprints.site.cart import pix
from app.blueprints.site.cart import frete
from app.blueprints.site.products import product_detail


@SiteBlueprint.context_processor
def inject_menu():
    """Injeta o menu de categorias em todos os templates do blueprint."""
    from app.model.category import ModelCategory
    return dict(menu=ModelCategory.get_menu())
