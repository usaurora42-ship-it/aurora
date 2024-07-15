# encoding: utf-8
import re
import os 
import base64
import json
from flask import Flask, render_template, make_response, send_file, request, jsonify
from app.blueprints.site import SiteBlueprint
from os.path import join, dirname, realpath
from werkzeug.utils import secure_filename

from app import logging
from app import environment
from app.model.products import ModelProduct
from app.model.category import ModelCategory
from app.model.baskets import ModelBasket
from app.model.enum import StatusEnum
<<<<<<< HEAD
from app.model.basket_products import ModelBasketProduct
=======
>>>>>>> 34269319e32e9a4130e037742af7f2222682b6ee


LOGGER = logging.getLogger(__name__)
app = Flask(__name__)
app.config['UPLOAD_PATH'] = os.path.dirname(os.path.abspath(__file__)) + '\\uploads'

def descriptions_get():    
    # query categories    
    query_category = ModelCategory.query.with_entities(
        ModelCategory.id,
        ModelCategory.description
    ).filter_by(
        status=StatusEnum.enabled,
        category_type=2
    ).order_by(ModelCategory.description)

    descriptions = query_category.all()

    return descriptions

def products_get():    
    # query products    
    query_products = ModelProduct.query.with_entities(
        ModelProduct.id,
        ModelProduct.name
    ).filter_by(
        status=StatusEnum.enabled
    ).order_by(ModelProduct.description)

    products = query_products.all()

    return products

@SiteBlueprint.route('/baskets/baskets', methods=['GET'])
def baskets_get():
    descriptions = descriptions_get()
    products = products_get()
    return render_template('/baskets/baskets.html', descriptions=descriptions, products=products)


@SiteBlueprint.route('/baskets/baskets', methods=['POST'])	
def baskets_post():  
    data = request.form.to_dict() or {}     

    
    file = request.files['file'] # get file
    file.save(os.path.join(app.config['UPLOAD_PATH'], file.filename))
    directory_path = os.path.join(app.config['UPLOAD_PATH'], file.filename)

    descriptions = descriptions_get()
    products = products_get()  
<<<<<<< HEAD
   

     # query basket
    query_basket = ModelBasket.query.with_entities(
        ModelBasket.id    
    ).filter_by(
        status=StatusEnum.enabled
    )

    # query product 
    query_product = ModelProduct.query.with_entities(
        ModelProduct.id
    ).filter_by(
        status=StatusEnum.enabled
    ).join(ModelBasketProduct).join(ModelBasket).filter_by(
        status=StatusEnum.enabled
    )
=======


     # query basket
    query_basket = ModelBasket.query.with_entities(
        ModelBasket.description
    ).filter_by(
        status=StatusEnum.enabled
    )
>>>>>>> 34269319e32e9a4130e037742af7f2222682b6ee
    
    # instance models
    model_basket = ModelBasket()  
    
<<<<<<< HEAD
    
    try:       
=======
    try:
>>>>>>> 34269319e32e9a4130e037742af7f2222682b6ee
        
        #
        # GET OR CREATE BASKET
        #
        basket = query_basket.first()
<<<<<<< HEAD
        product = query_product.first()
        
=======

>>>>>>> 34269319e32e9a4130e037742af7f2222682b6ee
        
    # create basket
        #if basket is None:
        data_basket = {
            'description': data['description'],
<<<<<<< HEAD
            'category_id': data['category'],                
            'value': data['value'],
            'path': directory_path                
        }        

        basket = model_basket.create_basket(data_basket)

        # errors
=======
            'product_id': data['product'], 
            'category_id': data['category'],                
            'value': data['value'],
            'path': directory_path
        }        
           
        
        basket = model_basket.create_basket(data_basket)

        # error to create basket
           
>>>>>>> 34269319e32e9a4130e037742af7f2222682b6ee
        if basket is None:
            resp = make_response(render_template('baskets/baskets.html',
                        success=False,
                        errors=model_basket.errors,
<<<<<<< HEAD
                        data_input=data))
            resp.mimetype = 'text/html'
            return resp 

       
        
        # basket_products = query_basket.filter(
        #             ModelBasket.id == basket.id,
        #             ModelProduct.id == products.id
        #         ).first()

        product = request.values.getlist("product")

        for p in product:

            model_basket_product = ModelBasketProduct()


            data_basket_product = {
                'basket_id': basket.id,
                'product_id': p
            }

            basket_product = model_basket_product.create_basket_product(data_basket_product)

        # error to create basket           
        if basket_product is None:
            resp = make_response(render_template('baskets/baskets.html',
                        success=False,
                        errors=model_basket.errors,
=======
>>>>>>> 34269319e32e9a4130e037742af7f2222682b6ee
                        data_input=data))      
            resp.mimetype = 'text/html'
            return resp  
            
        # success response
        resp = make_response(render_template('baskets/baskets.html',                            
                                success=True,
                                errors=None,descriptions=descriptions, products=products))
        resp.mimetype = 'text/html'
        return resp
        

    except Exception as e:
            LOGGER.exception(e)
            resp = make_response(render_template('errors/500.html',                            
                                    success=False,
                                    errors=None))
            resp.mimetype = 'text/html'
            return resp, 500
