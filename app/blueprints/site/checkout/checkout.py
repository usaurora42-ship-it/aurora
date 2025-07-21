# encoding: utf-8
from datetime import datetime
from flask import Flask, render_template, make_response, request, jsonify, session
from app.blueprints.site import SiteBlueprint

from app import logging
import json
from app.model.enum import StatusEnum
from app.model.order import ModelOrder
from app.model.session import ModelSession
from app.model.cart import ModelCart

LOGGER = logging.getLogger(__name__)

  
@SiteBlueprint.route('/cart/checkout', methods=['POST'])
def checkout_cart():
    data = request.form.to_dict() or {} 

    if 'user_id' not in session:
         return 'Login necessário', 403

    cart = json.loads(request.cookies.get('cart', '{}'))
    


    # query session
    query_session = ModelSession.query.with_entities(
         ModelSession.id
    ).filter_by(
        status=StatusEnum.enabled
    )

    # query cart
    query_cart = ModelCart.query.with_entities(
        ModelCart.id
    ).filter_by(
        status=StatusEnum.enabled
    )
   

    #instance model session
    model_session = ModelSession()
    model_cart = ModelCart() 

    try:
         # create session
        #if session is None:

        session = query_session.first()
        session = ModelSession(user_id=session['user_id'], date_create=datetime.now())

        #
        # GET OR CREATE CART
        #
        cart = query_cart.first()

       
    # create cart
        #if cart is None:
        for product_id, quantity in cart.itens():
            data_cart = {
                'product_id': data['product_id'],
                'quantity': data['quantity']
            }        
           
        
        product = model_product.create_product(data_product)

        # error to create product
           
        if product is None:
            resp = make_response(render_template('products/products.html',
                        success=False,
                        errors=model_product.errors,
                        data_input=data))      
            resp.mimetype = 'text/html'
            return resp  
            
            
        # success response
        resp = make_response(render_template('products/products.html',                            
                                success=True,
                                errors=None,descriptions=descriptions, units=units))
        resp.mimetype = 'text/html'
        return resp
        

    except Exception as e:
            LOGGER.exception(e)
            resp = make_response(render_template('errors/500.html',                            
                                    success=False,
                                    errors=None))
            resp.mimetype = 'text/html'
            return resp, 500
    

