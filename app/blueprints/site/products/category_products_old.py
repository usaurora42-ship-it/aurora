# encoding: utf-8
import re
import os 
import base64
from flask import Flask, render_template, make_response, send_file, request, jsonify
from app.blueprints.site import SiteBlueprint

from app import logging
from app import environment
from app.model.products import ModelProduct
from app.model.enum import StatusEnum
from app.model.product_category import ModelProductCategory


LOGGER = logging.getLogger(__name__)
app = Flask(__name__)


# print("diretoriooooooooooooooooooooo")
# print(os.getcwd() + '\\app\\static\\images\\products')
# print(os.path.basename(__file__))
# print(os.path.abspath(__file__))
# print(os.path.dirname(__file__))
# print(os.path.dirname(os.path.abspath(__file__)))
# print(dirname(dirname(dirname(os.path.abspath(__file__)))))


@SiteBlueprint.route('/products/category_products')    
def hello():
    
    return 'Hello world'
   