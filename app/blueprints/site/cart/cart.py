# encoding: utf-8
import re
import os 
import base64
import json
from flask import Flask, render_template, make_response, send_file, request
from app.blueprints.site import SiteBlueprint

from app import logging
from app import environment
from app.model.enum import StatusEnum
from app.model.cart import ModelCart

LOGGER = logging.getLogger(__name__)

# def breakfast_baskets_get():    
#     # query breakfast baskets    
#     query_breakfast = ModelBasket.query.with_entities(
#         ModelBasket.description,
#         ModelBasket.path,
#         ModelBasket.value
#     ).filter_by(
#         status=StatusEnum.enabled,
#         category_id=5
#     ).order_by(ModelBasket.description)

#     breakfast_baskets = query_breakfast.all()

#     return breakfast_baskets

# @SiteBlueprint.route('/baskets/breakfast_details', methods=['POST'])
# def breakfast_details_post():    
#     data = request.form.to_dict() or {} 

    
@SiteBlueprint.route('/cart/cart')
def cart_get():
    resp = make_response(render_template('cart/cart.html',
        success=False,
        errors=None,
        data_input=None))
    resp.mimetype = 'text/html'
    return resp 

@SiteBlueprint.route('/cart/cart', methods=['POST'])
def cart_post():  
    data = request.form.to_dict() or {}    

    # query cart
    query_cart = ModelCart.query.with_entities(
        ModelCart.id    
    ).filter_by(
        status=StatusEnum.enabled
    )
  
    # instance models
    model_cart = ModelCart()  
    
    
    try:       
        
        #
        # GET OR CREATE CART
        #
        cart = query_cart.first()
       
        
    # create cart
        #if cart is None:
        data_cart = {
            'value': data['value']               
        }        

        cart = model_cart.create_cart(data_cart)

        # errors
        if cart is None:
            resp = make_response(render_template('cart/cart.html',
                        success=False,
                        errors=model_cart.errors,
                        data_input=data))
            resp.mimetype = 'text/html'
            return resp 

       
        
        # basket_products = query_basket.filter(
        #             ModelBasket.id == basket.id,
        #             ModelProduct.id == products.id
        #         ).first()

        # product = request.values.getlist("product")

        # for p in product:

        #     model_basket_product = ModelBasketProduct()


        #     data_basket_product = {
        #         'basket_id': basket.id,
        #         'product_id': p
        #     }

        #     basket_product = model_basket_product.create_basket_product(data_basket_product)

        # # error to create basket           
        # if basket_product is None:
        #     resp = make_response(render_template('baskets/breakfast.html',
        #                 success=False,
        #                 errors=model_basket.errors,
        #                 data_input=data))      
        #     resp.mimetype = 'text/html'
        #     return resp  
            
        # success response
        resp = make_response(render_template('cart/cart.html',                            
                                success=True,
                                errors=None))
        resp.mimetype = 'text/html'
        return resp
        

    except Exception as e:
            LOGGER.exception(e)
            resp = make_response(render_template('errors/500.html',                            
                                    success=False,
                                    errors=None))
            resp.mimetype = 'text/html'
            return resp, 500
