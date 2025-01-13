# encoding: utf-8
import os
import yaml
import sys
import pytest
import redis
from os import environ
from flask import Flask, request, jsonify, render_template
from flask_cachebuster import CacheBuster
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_reverse_proxy import ReverseProxied
from flask_cors import CORS
from flask_mail import Mail
from flasgger import Swagger, LazyString, LazyJSONEncoder
from werkzeug import exceptions
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt
from flask_jwt_extended.exceptions import NoAuthorizationError, JWTDecodeError, RevokedTokenError, \
    FreshTokenRequired, WrongTokenError, CSRFError
from flask_log_request_id import RequestID, current_request_id
from flask_caching import Cache
from jwt.exceptions import ExpiredSignatureError, DecodeError, InvalidTokenError
from functools import wraps
import logging
import logging.config
from flask_session import Session
from flask_cors import CORS
# from flask_login import LoginManager
from redis import Redis


# APP
environment = os.environ.get('FLASK_ENV', 'local-testing')
FlaskApp = Flask(__name__, static_folder='static')
FlaskApp.wsgi_app = ReverseProxied(FlaskApp.wsgi_app)
FlaskApp.wsgi_app = ProxyFix(FlaskApp.wsgi_app, x_for=1, x_host=1)
CORS(FlaskApp)

FlaskApp.config["SESSION_PERMANENT"] = False
FlaskApp.config['SESSION_TYPE'] = 'redis'
FlaskApp.config['SESSION_REDIS'] = Redis.from_url('redis://localhost:6379')
# #SESSION_REDIS = redis.from_url(os.environ.get('SESSION_REDIS'))
# #sess = Session()
Session(FlaskApp)


# Config
FlaskApp.config.from_pyfile('config/default.cfg')
FlaskApp.config.from_pyfile('config/%s.cfg' % environment)


# LOGGER
# RequestID(FlaskApp)
with FlaskApp.open_resource('config/logging.yml') as f:
    config_data = yaml.safe_load(f.read())
    logging.config.dictConfig(config_data)
    f.close()
LOGGER = logging.getLogger(__name__)

# Email
mail = Mail(FlaskApp)

# Cache
cache = Cache()
cache.init_app(FlaskApp)


# Session
# login_manager = LoginManager(FlaskApp)
# login_manager.init_app(FlaskApp)
#sess.init_app(FlaskApp)

# @FlaskApp.after_request
# def add_header(response):
#     response.headers['X-RequestID'] = current_request_id()
#     return response

@FlaskApp.errorhandler(exceptions.InternalServerError)
def handle_bad_request(e):
    LOGGER.error('Internal Error: %r' % e)
    return {
        'errors': {
            'server': [
                'internal error', 'sorry, something went wrong',
                'please, report this error to api administrator with your request data',
                'contact by email: api@robobanker.com.br'
            ]
        }
    }, 500


# CORS
if environment == 'development' or environment == 'testing' or environment == 'local-testing':
    CORS(FlaskApp)

# Cache
cache_config = {'extensions': ['.js', '.css'], 'hash_size': 5}
cache_buster = CacheBuster(config=cache_config)
cache_buster.init_app(FlaskApp)

# Minify
#minify(app=FlaskApp, js=False, cssless=False)

# Swagger DOC
FlaskApp.json_encoder = LazyJSONEncoder


# DataBase
db = SQLAlchemy(app=FlaskApp)
from app.model import *

migrate = Migrate(FlaskApp, db)

# Database Fixtures
from app.model.fixture import ModelFixtures

#
# COMMANDS
#
@FlaskApp.cli.command('fixtures')
def fixtures():
    fixture = ModelFixtures()
    fixture.countries()
    fixture.languages()
    fixture.currencies()


@FlaskApp.cli.command('test')
def test():
    sys.exit(pytest.main(['-v', 'app/tests']))


""""
# JWT
jwt = JWTManager(FlaskApp)

def jwt_type_maybe(valids):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()

                if claims['type'] in valids or ('all' in valids and '_confirm' not in claims['type']):
                    return fn(*args, **kwargs)
                else:
                    return {'errors': {'jwt': ['forbidden for user token']}}, 403

            except Exception as e:
                pass

            return fn(*args, **kwargs)
        return wrapper
    return decorator

def jwt_type_required(valids, accept_expired=False, optional=False):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request(optional=optional)
            except (JWTDecodeError, DecodeError):
                return {'errors': {'jwt': ['jwt decode error']}}, 401
            except NoAuthorizationError:
                return {'errors': {'jwt': ['request unauthorized, please check your jwt']}}, 401
            except RevokedTokenError:
                return {'errors': {'jwt': ['this jwt was revoked']}}, 401
            except FreshTokenRequired:
                return {'errors': {'jwt': ['please, refresh your jwt']}}, 401
            except CSRFError:
                return {'errors': {'jwt': ['invalid request CSRF']}}, 401
            except (ExpiredSignatureError):
                if accept_expired is True:
                    return fn(*args, **kwargs)
                else:
                    return {'errors': {'jwt': ['expired token']}}, 401
            except (WrongTokenError, InvalidTokenError):
                return {'errors': {'jwt': ['this jwt is wrong, invalid or missing']}}, 401
            except Exception as e:
                LOGGER.exception(e)
                return {'errors': {'jwt': ['an unexpected error occured while validating your jwt']}}, 401

            claims = get_jwt()

            if optional is True or (claims['type'] in valids or ('all' in valids and '_confirm' not in claims['type'])):
               return fn(*args, **kwargs)
            else:
                return {'errors': {'jwt': ['forbidden for this user token']}}, 403

        return wrapper
    return decorator

@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(header, payload):
    jti = payload['jti']
    sub = payload['sub']
    return ModelRevokeToken().query.filter_by(
        jti=jti,
        sub=sub,
        token_status='revoked'
    ).count() > 0

@jwt.revoked_token_loader
def revoked_token_callback(header, payload):
    return jsonify({'errors': {'jwt': ['token revoked']}}), 401


@jwt.expired_token_loader
def expired_token_callback(header, payload):
    return jsonify({'errors': {'jwt': ['the token has expired']}}), 401


@jwt.invalid_token_loader
def invalid_token_callback(token):
    return jsonify({'errors': {'jwt': ['invalid token']}}), 400


@FlaskApp.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
    
@FlaskApp.errorhandler(exceptions.InternalServerError)
def handle_bad_request(e):
    LOGGER.error('Internal Error: %r' % e)
    return {
        'errors': {
            'server': [
                'Internal Error. Sorry, something went wrong',
                'please, report this error to api administrator with your request data',
                'contact by email: api@elasbank.com.br'
            ]
        }
    }, 500
"""

# API
api = Api(FlaskApp)

# Home
from app.home import Home
""" , Version, ClientIp """
api.add_resource(Home, '/api')
""" api.add_resource(Version, '/api/version')
api.add_resource(ClientIp, '/api/client-ip') """

#
# BluePrints
# 
from app.blueprints.site import SiteBlueprint
FlaskApp.register_blueprint(SiteBlueprint)

""" from app.blueprints.common import CommonBlueprint
FlaskApp.register_blueprint(CommonBlueprint, url_prefix='/api')

from app.blueprints.partner import PartnerBlueprint
FlaskApp.register_blueprint(PartnerBlueprint, url_prefix='/api')

from app.blueprints.client import ClientBlueprint
FlaskApp.register_blueprint(ClientBlueprint, url_prefix='/api')

from app.blueprints.bank import BankBlueprint
FlaskApp.register_blueprint(BankBlueprint, url_prefix='/api')

from app.blueprints.broker import BrokerBlueprint
FlaskApp.register_blueprint(BrokerBlueprint, url_prefix='/api')

from app.blueprints.system import SystemBlueprint
FlaskApp.register_blueprint(SystemBlueprint, url_prefix='/api')

from app.blueprints.third_party import ThirdPartyBlueprint
FlaskApp.register_blueprint(ThirdPartyBlueprint, url_prefix='/api')

from app.blueprints.pms import PMSBlueprint
FlaskApp.register_blueprint(PMSBlueprint, url_prefix='/api')

from app.blueprints.exchange_currency import ExchangeCurrencyBlueprint
FlaskApp.register_blueprint(ExchangeCurrencyBlueprint, url_prefix='/api')

from app.blueprints.loan import LoanBlueprint
FlaskApp.register_blueprint(LoanBlueprint, url_prefix='/api')

from app.blueprints.partnership import PartnerShipBlueprint
FlaskApp.register_blueprint(PartnerShipBlueprint, url_prefix='/api') 
 """