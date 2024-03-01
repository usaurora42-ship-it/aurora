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
        status=StatusEnum.enabled,
        document=data['document']
    )
    
    # query phone
    # query_phone = ModelPhone.query.with_entities(
    #     ModelPhone.id
    # ).filter(
    #     status=StatusEnum.enabled
    # ).join(ModelClient).filter_by(
    #     status=StatusEnum.enabled
    # ).first()

    # instance models
    model_client = ModelClient()
    # model_phone = ModelPhone()
    # model_client_phone = ModelClientPhone()

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
        """ phone = query_phone.filter(
            ModelPhone.code_area == data['code_area'],
            ModelPhone.code_country == data['code_country'],
            ModelPhone.number == data['number'],
            ModelClient.id == client.id
        ).first()

        # create client phone
        if phone is None:
            data_phone = {
                'code_country': data['code_country'],
                'code_area': data['code_area'],
                'number': data['number']
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
                return resp """
    
        #
        # GET OR CREATE CLIENT ADDRESS
        #


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


    