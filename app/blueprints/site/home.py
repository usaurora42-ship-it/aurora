# encoding: utf-8
from flask import render_template, make_response, request, session, redirect

from app.blueprints.site import SiteBlueprint
from app import logging
from app import environment
from app.model.products import ModelProduct
from app.model.enum import StatusEnum

LOGGER = logging.getLogger(__name__)


def products_list_get():
    #query products
    query_products = ModelProduct.query.with_entities(
        ModelProduct.description,
        ModelProduct.name,
        ModelProduct.value
    ).filter_by(
        status=StatusEnum.enabled
    ).order_by(ModelProduct.description)

    products = query_products.all()    

    page = request.args.get('page', 1, type=int) 
    posts = query_products.paginate(page=page, per_page=4, error_out=False)
    return render_template('/home.html', products_list_get=products, items=posts.items, pagination=posts)

@SiteBlueprint.route('/')
def index():       
    resp = make_response(
        render_template('/home.html', success=False, email_error=False, environment=environment))
    resp.mimetype = 'text/html'
    return resp



