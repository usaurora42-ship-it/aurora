# encoding: utf-8
import re
import os 
import base64
from flask import Flask, render_template, make_response, send_file, request, jsonify
from app.blueprints.site import SiteBlueprint
from os.path import join, dirname, realpath
from werkzeug.utils import secure_filename

from app import logging
from app.lib.auth import admin_required
from app import environment
from app.model.products import ModelProduct
from app.model.category import ModelCategory
from app.model.product_category import ModelProductCategory
from app.model.units import ModelUnit
from app.model.enum import StatusEnum


LOGGER = logging.getLogger(__name__)
app = Flask(__name__)
app.config['UPLOAD_PATH'] = os.getcwd() + '\\app\\static\\images\\products'


def categories_get():    
    query_category = ModelCategory.query.with_entities(
        ModelCategory.id,
        ModelCategory.description
    ).filter_by(
        status=StatusEnum.enabled
    ).order_by(ModelCategory.description)
    return query_category.all()

def units_get():    
    query_unit = ModelUnit.query.with_entities(
        ModelUnit.id,
        ModelUnit.description
    ).filter_by(
        status=StatusEnum.enabled        
    ).order_by(ModelUnit.description)
    return query_unit.all()

def products_get():    
    query_products = ModelProduct.query.with_entities(
        ModelProduct.id,
        ModelProduct.name
    ).filter_by(
        status=StatusEnum.enabled
    ).order_by(ModelProduct.description)
    return query_products.all()


@SiteBlueprint.route('/products/products', methods=['GET'])
@admin_required
def product_get():
    categories = categories_get()
    units = units_get()
    products = products_get()
    return render_template('/products/products.html', 
                           categories=categories,  
                           units=units,            
                           products=products)


@SiteBlueprint.route('/products/products', methods=['POST'])	
def products_post():  
    data = request.form.to_dict() or {}

    print("=" * 60)
    print(">>> [POST /products] DADOS RECEBIDOS:", data)
    print(">>> [POST /products] ARQUIVO:", request.files.get('file'))
    print("=" * 60)

    categories = categories_get()
    products   = products_get()
    units      = units_get()

    model_product          = ModelProduct()  
    model_product_category = ModelProductCategory()

    def render_error(errors):
        print(">>> [ERRO] Erros retornados:", errors)
        resp = make_response(render_template('products/products.html',
            success=False,
            errors=errors,
            data_input=data,
            categories=categories,
            units=units,
            products=products))
        resp.mimetype = 'text/html'
        return resp

    try:
        # ── Valida arquivo ─────────────────────────────────────────
        file = request.files.get('file')
        if not file or file.filename == '':
            print(">>> [ERRO] Nenhum arquivo enviado")
            return render_error({'file': 'Selecione uma imagem para o produto.'})

        # ── Converte value ─────────────────────────────────────────
        value_raw = data.get('value', '').strip()
        try:
            value = float(value_raw.replace(',', '.'))
        except ValueError:
            print(">>> [ERRO] value inválido:", value_raw)
            return render_error({'value': f'Valor inválido: "{value_raw}". Use números (ex: 56,00).'})

        # ── Salva imagem ───────────────────────────────────────────
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_PATH'], filename)
        print(">>> [ARQUIVO] Salvando em:", save_path)
        file.save(save_path)

        # Monta path relativo (\static/...)
        directory_path = save_path
        for sep in ['\\static', '/static']:
            n = save_path.find(sep)
            if n != -1:
                directory_path = save_path[n:].replace('\\', '/')
                break

        print(">>> [ARQUIVO] Path relativo:", directory_path)

        # ── Monta data_product ─────────────────────────────────────
        data_product = {
            'name':        data.get('name', '').strip(),
            'description': data.get('description', '').strip(),
            'value':       value,
            'size':        data.get('size', '').strip() or None,
            'unit_id':     int(data.get('unit', 0)),
            'path':        directory_path,
        }

        print(">>> [MODEL] data_product:", data_product)

        product = model_product.create_product(data_product)

        if product is None:
            print(">>> [ERRO] create_product falhou:", model_product.errors)
            return render_error(model_product.errors)

        print(">>> [OK] Produto criado id:", product.id)

        # ── Cria relação produto-categoria ─────────────────────────
        data_product_category = {
            'product_id':  product.id,
            'category_id': int(data.get('category', 0))
        }

        print(">>> [MODEL] data_product_category:", data_product_category)

        product_category = model_product_category.create_product_category(data_product_category)

        if product_category is None:
            print(">>> [ERRO] create_product_category falhou:", model_product_category.errors)
            return render_error(model_product_category.errors)

        print(">>> [OK] ProductCategory criado")

        # ── Sucesso ────────────────────────────────────────────────
        resp = make_response(render_template('products/products.html',
            success=True,
            errors=None,
            data_input=None,
            categories=categories,
            units=units,
            products=products_get()))
        resp.mimetype = 'text/html'
        return resp

    except Exception as e:
        print(">>> [EXCEPTION]", str(e))
        LOGGER.exception(e)
        resp = make_response(render_template('errors/500.html',
            success=False,
            errors=None))
        resp.mimetype = 'text/html'
        return resp, 500
