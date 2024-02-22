# encoding: utf-8
import re
from logging import debug
from flask import Blueprint, render_template, make_response, request, send_from_directory, current_app
import json
from urllib.request import urlopen

from app import logging
from app import environment
from app.model.client import ModelClient
from app.model.phones import ModelPhone
from app.model.address import ModelAddress
from app.model.gifted import ModelClientGifted


LOGGER = logging.getLogger(__name__)


SiteBlueprint = Blueprint('site_bp', 'site', url_prefix='')


@SiteBlueprint.route('/')
def index():
    resp = make_response(
        render_template('index.html', success=False, email_error=False, environment=environment))
    resp.mimetype = 'text/html'
    return resp

@SiteBlueprint.route('/cadastro')
def cad():
    resp = make_response(
        render_template('cadastro.html', success=False, email_error=False, environment=environment))
    resp.mimetype = 'text/html'
    return resp


@SiteBlueprint.route('/cadastro', methods=['POST'])
def create_register():
    data = request.form.to_dict() or {}

    LOGGER.info(json.dumps(data))

    # get client
    client = ModelClient.query.with_entities(
        ModelClient.id
    ).filter_by(
        uuid=data['client_uuid']
    ).first()

    if client is None:
        resp = make_response(render_template('cadastro.html',
                            success=False,
                            errosr={'client': ['client not found']},
                            name=data['name'],
                            typeperson=data['typeperson']))
        resp.mimetype = 'text/html'
        return resp 
    
    # get phone
    phone = ModelPhone.query.with_entities(
        ModelPhone.id
    ).filter_by(
        uuid=data['phone_uuid']
    ).first()

    if phone is None:
        resp = make_response(render_template('cadastro.html',
                            success=False,
                            errosr={'phone': ['phone not found']},
                            phone=data['phone']))
        resp.mimetype = 'text/html'
        return resp
    
    # get address
    address = ModelAddress.query.with_entities(
        ModelAddress.id
    ).first()

    if address is None:
        resp = make_response(render_template('cadastro.html',
                            success=False,
                            errosr={'address': ['address not found']},
                            address=data['address']))
        resp.mimetype = 'text/html'
        return resp
    
    # get gifted
    gifted = ModelClientGifted.query.with_entities(
        ModelClientGifted.id
    ).filter_by(
        uuid=data['gifted_uuid']
    ).first()

    if gifted is None:
        resp = make_response(render_template('cadastro.html',
                            success=False,
                            errosr={'gifted': ['gifted not found']},
                            gifted_name=data['gifted_name']))
        resp.mimetype = 'text/html'
        return resp 

    # create register
    register_data = {
        'client_id': client.id,
        'name': data['name'],
        'email': data['email'],
        'phone': re.sub(r'\D', '', data['phone']),
        'typeperson': data['typeperson'],
        'document': data['document'],
        'zipcode': data['zipcode'],
        'street': data['street'],
        'number': data['number'],
        'complement': data['complement'],
        'district': data['district'],
        'city': data['city'],
        'state': data['state'],
        'giftedname': data['giftedname'],
        'giftedphone': data['giftedphone'], 
        'giftedocasion': data['giftedocasion'],
        'giftedmessage': data['giftedmessage'],
        'signaturecard': data['signaturecard'],
        'datedelivery': data['datedelivery'],
        'timeslot': data['timeslot']      
        }

    # success response
    resp = make_response(render_template('cadastro.html',                            
                            success=True,
                            errors=False,
                            name=data['name']))
    resp.mimetype = 'text/html'
    return resp