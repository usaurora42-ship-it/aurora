# encoding: utf-8
from flask import Flask, render_template, make_response, request, jsonify
from app.blueprints.site import SiteBlueprint

from app import logging
from app import environment
import json
from app.model.enum import StatusEnum
from app.model.products import ModelProduct


LOGGER = logging.getLogger(__name__)

    
@SiteBlueprint.route('/cart/cart')
def cart_get():
    cart_cookie = request.cookies.get('cart')
    if not cart_cookie:
         return jsonify({'mensagem': 'Carrinho vazio', 'itens':[]})
    
    cart = json.loads(cart_cookie)
    products_ids = list(map(int, cart.keys()))
    products = ModelProduct.query.filter(ModelProduct.id.in_(products_ids)).all()

    itens = []
    for product in products:
         itens.append({
              'id': product.id,
              'name': product.name,
              'value': product.value,
              'quantity': cart[str(product.id)],
              'subtotal': cart[str(product.id)] * product.value
         })    

    return jsonify(itens)
 