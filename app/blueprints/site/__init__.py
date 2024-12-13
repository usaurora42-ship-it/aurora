# encoding: utf-8
from flask import Blueprint

SiteBlueprint = Blueprint('site_bp', 'site', url_prefix='')

from app.blueprints.site import home
from app.blueprints.site.client import signup, login
from app.blueprints.site.products import products
from app.blueprints.site.baskets import baskets, breakfast, breakfast_details
from app.blueprints.site.checkout import cart


