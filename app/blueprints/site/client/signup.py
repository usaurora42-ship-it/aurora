# encoding: utf-8
import re
from flask import render_template, make_response, request, session, redirect

from app.blueprints.site import SiteBlueprint

from app import logging
from app import environment
from app.model.client import ModelClient
from app.model.phones import ModelPhone
from app.model.address import ModelAddress
from app.model.client_phone import ModelClientPhone
from app.model.client_address import ModelClientAddress
from app.model.users import ModelUser
from app.model.countries import ModelCountry
from app.model.enum import StatusEnum
from flask_session import Session

LOGGER = logging.getLogger(__name__)


@SiteBlueprint.route('/client/signup')
def signup_get():
    from flask import session as flask_session

    # Pré-preenche com dados do checkout se vier de lá
    checkout_data = flask_session.get('checkout_data', {})
    data_input = None
    if checkout_data:
        data_input = {
            'email':         checkout_data.get('email', ''),
            'zip_code':      checkout_data.get('zip_code', ''),
            'street':        checkout_data.get('street', ''),
            'street_number': checkout_data.get('street_number', ''),
            'complement':    checkout_data.get('complement', ''),
            'district':      checkout_data.get('district', ''),
            'city':          checkout_data.get('city', ''),
            'state':         checkout_data.get('state', ''),
        }

    next_url = request.args.get('next', '/client/login')

    resp = make_response(render_template('client/signup.html',
        success=False,
        errors=None,
        data_input=data_input,
        next_url=next_url))
    resp.mimetype = 'text/html'
    return resp 


@SiteBlueprint.route('/client/signup', methods=['POST'])
def signup_post():
    data = request.form.to_dict() or {}

    # record the user name
    session["name"] = data['name']

    # ── Verifica se o e-mail já está cadastrado ──
    if data.get('email', '').strip():
        email_exists = ModelClient.query.filter_by(
            email=data['email'].strip().lower()
        ).first()
        if email_exists:
            resp = make_response(render_template('client/signup.html',
                        success=False,
                        errors={'email': ['Este e-mail já está cadastrado. Faça login ou use outro e-mail.']},
                        data_input=data))
            resp.mimetype = 'text/html'
            return resp

    # query client
    query_client = ModelClient.query.with_entities(
        ModelClient.id
    ).filter_by(
        #status=StatusEnum.enabled,
        document=data['document'].replace("-","").replace(".","").replace("/","")
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

    # query user 
    query_user = ModelUser.query.with_entities(
         ModelUser.client_id
    ).filter_by(
        status=StatusEnum.enabled
    ).join(ModelClient).filter_by(
        status=StatusEnum.enabled
    )

    # instance models
    model_client = ModelClient()
    model_phone = ModelPhone()
    model_client_phone = ModelClientPhone()
    model_address = ModelAddress()
    model_client_address = ModelClientAddress()
    model_user = ModelUser()

    try:

        #
        # GET OR CREATE CLIENT
        #
        client = query_client.first()

        # create client
        if client is None:
            data_client = {
                'document': data['document'].replace("-","").replace(".","").replace("/",""),
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
            ModelPhone.code_area == data['phone'][1:3],            
            ModelPhone.number == data['phone'][4:15].replace("-",""),
            ModelClient.id == client.id
        ).first()


        # create client phone
        if phone is None:
            data_phone = {
                'code_country': '55', #data['phone'][0:2]'',
                'code_area': data['phone'][1:3],
                'number': data['phone'][4:15].replace("-","")
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

        # country fixo como Brasil
        model_country = ModelCountry()
        country_id = model_country.get_country_id('BRA')
        data['country_id'] = country_id

        # create client address
        if address is None:
            data_address = {
                'state': data['state'],
                'city': data['city'],
                'district': data['district'],
                'zip_code': data['zip_code'].replace("-",""),
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


        user = query_user.filter(
            ModelClient.id == client.id
        ).first()        


        # # create client user
        if user is None:
            data_client_user = {
                'client_id': client.id,
                'user_name': data['user_name'],
                'pwd': data['pwd']         
        }      
       
        
        user = model_user.create_user(data_client_user)
        
        # errors
        if user is None:
            resp = make_response(render_template('client/signup.html',
                        success=False,
                        errors=model_address.errors,
                            data_input=data))

            resp.mimetype = 'text/html'
            return resp 
        
        # create client x user
        data_client_user = {
            'user_id': user.id,
            'client_id': client.id            
        }         
        
        # redireciona para next ou login
        next_url = request.args.get('next') or request.form.get('next') or '/client/login'
        return redirect(next_url)

    except Exception as e:
            LOGGER.exception(e)
            resp = make_response(render_template('errors/500.html',                            
                                    success=False,
                                    errors=None))
            resp.mimetype = 'text/html'
            return resp, 500


    