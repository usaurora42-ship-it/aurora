# encoding: utf-8
from flask import Blueprint

SiteBlueprint = Blueprint('site_bp', 'site', url_prefix='')

from app.blueprints.site import home
from app.blueprints.site.client import signup, login
from app.blueprints.site.products import products
<<<<<<< HEAD
from app.blueprints.site.baskets import baskets, breakfast


=======
from app.blueprints.site.baskets import baskets
>>>>>>> 34269319e32e9a4130e037742af7f2222682b6ee
