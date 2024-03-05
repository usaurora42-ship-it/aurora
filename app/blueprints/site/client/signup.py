# encoding: utf-8
import re
from flask import render_template, make_response, request

from app.blueprints.site import SiteBlueprint

from app import logging
from app import environment
from app.model.client import ModelClient
from app.model.phones import ModelPhone
from app.model.address import ModelAddress
from app.model.gifted import ModelClientGifted
from app.model.client_phone import ModelClientPhone
from app.model.client_address import ModelClientAddress
from app.model.countries import ModelCountry
from app.model.enum import StatusEnum


LOGGER = logging.getLogger(__name__)


@SiteBlueprint.route('/client/signup')
def signup_get():
    resp = make_response(render_template('client/signup.html',
        success=False,
        errors=None,
        data_input=None))
    resp.mimetype = 'text/html'
    return resp 


@SiteBlueprint.route('/client/signup', methods=['POST'])
def signup_post():
    data = request.form.to_dict() or {}

    # query client
    query_client = ModelClient.query.with_entities(
        ModelClient.id
    ).filter_by(
        #status=StatusEnum.enabled,
        document=data['document']
    )
    
    # query phone 
    query_phone = ModelPhone.query.with_entities(
        ModelPhone.id
    ).filter_by(
        status=StatusEnum.enabled
    ).join(ModelClientPhone).join(ModelClient).filter_by(
        status=StatusEnum.enabled
    )

    # query address 
    query_address = ModelAddress.query.with_entities(
        ModelAddress.id
    ).filter_by(
        status=StatusEnum.enabled
    ).join(ModelClientAddress).join(ModelClient).filter_by(
        status=StatusEnum.enabled
    )

    # instance models
    model_client = ModelClient()
    model_phone = ModelPhone()
    model_client_phone = ModelClientPhone()
    model_address = ModelAddress()
    model_client_address = ModelClientAddress()

    try:

        #
        # GET OR CREATE CLIENT
        #
        client = query_client.first()

        # create client
        if client is None:
            data_client = {
                'document': data['document'],
                'email': data['email'],
                'name': data['name'],                
                'type': data['typeperson']
            }

            client = model_client.create_client(data_client)

            # error to create client
            if client is None:
                resp = make_response(render_template('client/signup.html',
                            success=False,
                            errors=model_client.errors,
                            data_input=data))
                resp.mimetype = 'text/html'
                return resp 
            
        #
        # GET OR CREATE A CLIENT PHONE
        #
        phone = query_phone.filter(
            ModelPhone.code_country == '55', #data['phone'][0:2]'',
            ModelPhone.code_area == data['phone'][0:2],            
            ModelPhone.number == data['phone'][2:12],
            ModelClient.id == client.id
        ).first()

        # create client phone
        if phone is None:
            data_phone = {
                'code_country': '55', #data['phone'][0:2]'',
                'code_area': data['phone'][0:2],
                'number': data['phone'][2:12]
            }

            phone = model_phone.create_phone(data_phone)
            
            # errors
            if phone is None:
                resp = make_response(render_template('client/signup.html',
                            success=False,
                            errors=model_phone.errors,
                            data_input=data))
                resp.mimetype = 'text/html'
                return resp 
            
            # create client x phone
            data_client_phone = {
                'client_id': client.id,
                'phone_id': phone.id
            }

            client_phone = model_client_phone.create_client_phone(data_client_phone)

            # errors
            if client_phone is None:
                resp = make_response(render_template('client/signup.html',
                            success=False,
                            errors=model_client_phone.errors,
                            data_input=data))
                resp.mimetype = 'text/html'
                return resp
    
        #
        # GET OR CREATE CLIENT ADDRESS
        #
        address = query_address.filter(            
            ModelClient.id == client.id
        ).first()

        # country
        data_country = data.pop('country')[0:3]
        model_country = ModelCountry()
        country_id = model_country.get_country_id(data_country)
        if country_id is None:
            return {
                'errors': {
                    'country': ['country %s unavalible' % data_country]
                }
            }, 400

        data['country_id'] = country_id

        # create client address
        if address is None:
            data_address = {
                'state': data['state'],
                'city': data['city'],
                'district': data['district'],
                'zip_code': data['zip_code'],
                'street': data['street'],
                'street_number': data['street_number'],
                'complement': data['complement'],
                'country_id': data['country_id'] 
            }

            address = model_address.create_address(data_address)
            
            # errors
            if address is None:
                resp = make_response(render_template('client/signup.html',
                            success=False,
                            errors=model_address.errors,
                            data_input=data))

                resp.mimetype = 'text/html'
                return resp 
            
            # create client x address
            data_client_address = {
                'client_id': client.id,
                'address_id': address.id
            }

            client_address = model_client_address.create_client_address(data_client_address)

            # errors
            if client_address is None:
                resp = make_response(render_template('client/signup.html',
                            success=False,
                            errors=model_client_phone.errors,
                            data_input=data))
                resp.mimetype = 'text/html'
                return resp

        # success response
        resp = make_response(render_template('client/signup.html',                            
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


    