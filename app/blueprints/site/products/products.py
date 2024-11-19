# encoding: utf-8
import re
import os 
import base64
from flask import Flask, render_template, make_response, send_file, request, jsonify
from app.blueprints.site import SiteBlueprint
from os.path import join, dirname, realpath
from werkzeug.utils import secure_filename

from app import logging
from app import environment
from app.model.products import ModelProduct
from app.model.category import ModelCategory
from app.model.units import ModelUnit
from app.model.enum import StatusEnum


LOGGER = logging.getLogger(__name__)
app = Flask(__name__)
app.config['UPLOAD_PATH'] = os.getcwd() + '\\app\\static\\images\\products'

# print("diretoriooooooooooooooooooooo")
# print(os.getcwd() + '\\app\\static\\images\\products')
# print(os.path.basename(__file__))
# print(os.path.abspath(__file__))
# print(os.path.dirname(__file__))
# print(os.path.dirname(os.path.abspath(__file__)))
# print(dirname(dirname(dirname(os.path.abspath(__file__)))))

def descriptions_get():    
    # query categories    
    query_category = ModelCategory.query.with_entities(
        ModelCategory.id,
        ModelCategory.description
    ).filter_by(
        status=StatusEnum.enabled#,
        #category_type=1
    ).order_by(ModelCategory.description)

    descriptions = query_category.all()

    return descriptions

def units_get():    
    # query units
    query_unit = ModelUnit.query.with_entities(
        ModelUnit.id,
        ModelUnit.description
    ).filter_by(
        status=StatusEnum.enabled        
    ).order_by(ModelUnit.description)

    units = query_unit.all()

    return units

@SiteBlueprint.route('/products/products', methods=['GET'])
def products_get():
    descriptions = descriptions_get()
    units = units_get()
    return render_template('/products/products.html', descriptions=descriptions, units=units)
    # print(descriptions)
        #return render_template('product/product.html',descriptions=descriptions)

        # for category in query_category.all():
        #     result_category = category.description
        #     print(result_category)
        # return render_template('product/product.html',result_category=result_category)
        # resp = make_response(render_template('products/products.html',
        #     success=False,
        #     errors=None,
        #     data_input=None,
        #     descriptions=descriptions,
        #     units=units))
        # resp.mimetype = 'text/html'
        # return resp 
        

@SiteBlueprint.route('/products/products', methods=['POST'])	
def products_post():  
    data = request.form.to_dict() or {}     

    
    file = request.files['file'] # get file
    file.save(os.path.join(app.config['UPLOAD_PATH'], file.filename))
    directory_path = os.path.join(app.config['UPLOAD_PATH'], file.filename)

    descriptions = descriptions_get()
    units = units_get()
    #print(descriptions)
    #print(units)
    #return render_template('/products/products.html', descriptions=descriptions, units=units)

    # query product
    query_product = ModelProduct.query.with_entities(
        ModelProduct.description
    ).filter_by(
        status=StatusEnum.enabled
    )
    
    # for product in query_product.all():
    #       result = ModelCategory.get_dict(product)
    #       print(result)

    # # query categories
    # query_category = ModelCategory.query.with_entities(
    #      ModelCategory.description
    # ).filter_by(
    #     status=StatusEnum.enabled
    # )


    # for category in query_category.all():
    #      result = ModelCategory.get_dict(category)
    #      print(result)

           
    
    # instance models
    model_product = ModelProduct()  
    
    try:
        
    #return f'Uploaded: {file.filename}' 
        #
        # GET OR CREATE PRODUCT
        #
        product = query_product.first()

       
    # create product
        #if product is None:
        data_product = {
            'name': data['name'],
            'description': data['description'],
            'category_id': data['category'],                
            'value': data['value'],
            'size': data['size'],
            'unit_id': data['unit'],
            'path': directory_path
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
