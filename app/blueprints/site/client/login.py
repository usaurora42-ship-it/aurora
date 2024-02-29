# encoding: utf-8
from flask import render_template, make_response, request

from app.blueprints.site import SiteBlueprint

from app import logging


LOGGER = logging.getLogger(__name__)


@SiteBlueprint.route('/client/login')
def login_get():
    resp = make_response(render_template('client/login.html',
        success=False,
        errors=None,
        data_input=None))
    resp.mimetype = 'text/html'
    return resp 


@SiteBlueprint.route('/client/login',  methods=['POST'])
def login_post():
    # TODO: login
    resp = make_response(render_template('client/login.html',
        success=False,
        errors=None,
        data_input=None))
    resp.mimetype = 'text/html'
    return resp
