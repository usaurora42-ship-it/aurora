# encoding: utf-8
import re
import os
from flask import Flask, flash, render_template, make_response, request, redirect, url_for, send_from_directory
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
from app.blueprints.site import SiteBlueprint
from werkzeug.utils import secure_filename
from flask_uploads import UploadSet, IMAGES, configure_uploads

from app import logging
from app import environment
from app.model.products import ModelProduct
from app.model.category import ModelCategory
from app.model.units import ModelUnit
from app.model.enum import StatusEnum


LOGGER = logging.getLogger(__name__)
app = Flask(__name__)
app.config['SECRET_KEY'] = 'asldfkjlj'
app.config['UPLOADED_PHOTOS_DEST'] = 'uploads'

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

class UploadForm(FlaskForm):
	photo = FileField(
		validators=[
			FileAllowed(photos, 'Somente imagens são permitidas'),
			FileRequired('O campo não pode estar vazio')
        ]
    )
	submit = SubmitField('Upload')
     
@app.route('/images/products/<filename>')
def get_file(filename):
	return send_from_directory(app.config['UPLOADED_PHOTOS_DEST'], filename)

@SiteBlueprint.route('/products/products')
def products_get():

    # query categories
    query_category = ModelCategory.query.with_entities(
         ModelCategory.id,
         ModelCategory.description
    ).filter_by(
        status=StatusEnum.enabled
    ).order_by(ModelCategory.description)

    descriptions = query_category.all()

    # query units
    query_unit = ModelUnit.query.with_entities(
         ModelUnit.id,
         ModelUnit.description
    ).filter_by(
        status=StatusEnum.enabled
    ).order_by(ModelUnit.description)

    units = query_unit.all()

   # print(descriptions)
    #return render_template('product/product.html',descriptions=descriptions)

    # for category in query_category.all():
    #     result_category = category.description
    #     print(result_category)
       # return render_template('product/product.html',result_category=result_category)
    resp = make_response(render_template('products/products.html',
        success=False,
        errors=None,
        data_input=None,
        descriptions=descriptions,
        units=units))
    resp.mimetype = 'text/html'
    return resp 

@SiteBlueprint.route('/products/products', methods=['GET', 'POST'])	
def upload_image():
	form = UploadForm()
	if form.validate_on_submit():
		filename = photos.save(form.photo.data)
		file_url = url_for('get_file', filename=filename)
	else:
		file_url = None
	return render_template('products/products.html', form=form, file_url=file_url)

def products_post():      

    data = request.form.to_dict() or {}

    # query product
    query_product = ModelProduct.query.with_entities(
        ModelProduct.id
    ).filter_by(
        status=StatusEnum.enabled
    ) 


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

        #
        # GET OR CREATE PRODUCT
        #
        product = query_product.first()

        # create product
        if product is None:
            data_product = {
                'name': data['name'],
                'description': data['description'],
                'category_id': data['category'],                
                'value': data['value'],
                'size': data['size'],
                'unit_id': data['unit']
            }

            product = model_product.create_product(data_product)

            # error to create product
            
            if product is None:
                resp = make_response(render_template('products/products.html',
                            success=False,
                            errors=model_product.errors,
                            data_input=data,
                            form=form, 
                            file_url=file_url))      
                resp.mimetype = 'text/html'
                return resp 
            
            # success response
            resp = make_response(render_template('products/products.html',                            
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


    