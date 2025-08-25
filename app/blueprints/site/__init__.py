# encoding: utf-8
from flask import Blueprint

SiteBlueprint = Blueprint('site_bp', 'site', url_prefix='')

from app.blueprints.site import home
from app.blueprints.site.client import signup, login
from app.blueprints.site.products import products
from app.blueprints.site.products import category_products
from app.blueprints.site.hello import hello


