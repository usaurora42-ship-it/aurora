# encoding: utf-8
from flask import render_template, make_response

from app.blueprints.site import SiteBlueprint
from app import logging
from app import environment



LOGGER = logging.getLogger(__name__)


@SiteBlueprint.route('/')
def index():
    resp = make_response(
        render_template('home.html', success=False, email_error=False, environment=environment))
    resp.mimetype = 'text/html'
    return resp
