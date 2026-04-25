# encoding: utf-8
import re
import os 
import base64
import json
from flask import Flask, render_template, make_response, send_file, request
from app.blueprints.site import SiteBlueprint

from app import logging
from app import environment
from app.model.products import ModelProduct
from app.model.enum import StatusEnum
from app.model.product_category import ModelProductCategory
from app.model.category import ModelCategory
from app.model.units import ModelUnit



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


def categories_products_get():    
    # query categories    
    query_category = ModelCategory.query.with_entities(
        ModelCategory.id,
        ModelCategory.description
    ).filter_by(
        status=StatusEnum.enabled
    ).order_by(ModelCategory.description)

    categories = query_category.all()

    return categories

def units_products_get():    
    # query units
    query_unit = ModelUnit.query.with_entities(
        ModelUnit.id,
        ModelUnit.description
    ).filter_by(
        status=StatusEnum.enabled        
    ).order_by(ModelUnit.description)

    units = query_unit.all()

    return units

def products_p_get():    
    # query products    
    query_products = ModelProduct.query.with_entities(
        ModelProduct.id,
        ModelProduct.name
    ).filter_by(
        status=StatusEnum.enabled
    ).order_by(ModelProduct.description)

    products = query_products.all()

    return products


@SiteBlueprint.route('/products/category_products', methods=['GET'])
def category_product_get():
    categories = categories_products_get()
    units = units_products_get()
    products = products_p_get()

    #query products
    query_products = ModelProduct.query.with_entities(
        ModelProduct.id,
        ModelProduct.description, 
        ModelProduct.path,
        ModelProduct.value,
    ).filter_by(
        status=StatusEnum.enabled
    ).order_by(ModelProduct.description)

    list_products = query_products.all()  

    page = request.args.get('page', 1, type=int) 
    posts = query_products.paginate(page=page, per_page=16, error_out=False)

    return render_template('/products/category_products.html', categories=categories, units=units, products=products, list_products=list_products, items=posts.items, pagination=posts)

    


  
# @SiteBlueprint.route('/baskets/breakfast', methods=['POST'])	
# def baskets_post():  
#     data = request.form.to_dict() or {}     

#     posts = Post.query.paginate(page=page, per_page=10, error_out=False)
   

#      # query basket
#     query_basket = ModelBasket.query.with_entities(
#         ModelBasket.id    
#     ).filter_by(
#         status=StatusEnum.enabled
#     )

#     # query product 
#     query_product = ModelProduct.query.with_entities(
#         ModelProduct.id
#     ).filter_by(
#         status=StatusEnum.enabled
#     ).join(ModelBasketProduct).join(ModelBasket).filter_by(
#         status=StatusEnum.enabled
#     )
    
#     # instance models
#     model_basket = ModelBasket()  
    
    
#     try:       
        
#         #
#         # GET OR CREATE BASKET
#         #
#         basket = query_basket.first()
#         product = query_product.first()
        
        
#     # create basket
#         #if basket is None:
#         data_basket = {
#             'description': data['description'],
#             'category_id': data['category'],                
#             'value': data['value'],
#             'path': directory_path                
#         }        

#         basket = model_basket.create_basket(data_basket)

#         # errors
#         if basket is None:
#             resp = make_response(render_template('baskets/breakfast.html',
#                         success=False,
#                         errors=model_basket.errors,
#                         data_input=data))
#             resp.mimetype = 'text/html'
#             return resp 

       
        
#         # basket_products = query_basket.filter(
#         #             ModelBasket.id == basket.id,
#         #             ModelProduct.id == products.id
#         #         ).first()

#         product = request.values.getlist("product")

#         for p in product:

#             model_basket_product = ModelBasketProduct()


#             data_basket_product = {
#                 'basket_id': basket.id,
#                 'product_id': p
#             }

#             basket_product = model_basket_product.create_basket_product(data_basket_product)

#         # error to create basket           
#         if basket_product is None:
#             resp = make_response(render_template('baskets/breakfast.html',
#                         success=False,
#                         errors=model_basket.errors,
#                         data_input=data))      
#             resp.mimetype = 'text/html'
#             return resp  
            
#         # success response
#         resp = make_response(render_template('baskets/breakfast.html',                            
#                                 success=True,
#                                 errors=None,descriptions=descriptions, products=products))
#         resp.mimetype = 'text/html'
#         return resp
        

#     except Exception as e:
#             LOGGER.exception(e)
#             resp = make_response(render_template('errors/500.html',                            
#                                     success=False,
#                                     errors=None))
#             resp.mimetype = 'text/html'
#             return resp, 500
