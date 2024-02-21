# encoding: utf-8
import re
from logging import debug
from flask import Blueprint, render_template, make_response, request, send_from_directory, current_app
import json
from urllib.request import urlopen

from app import logging
from app import environment


LOGGER = logging.getLogger(__name__)


SiteBlueprint = Blueprint('site_bp', 'site', url_prefix='')


@SiteBlueprint.route('/')
def index():
    resp = make_response(
        render_template('index.html', success=False, email_error=False, environment=environment))
    resp.mimetype = 'text/html'
    return resp

@SiteBlueprint.route('/cadastro')
def terms():
    resp = make_response(
        render_template('cadastro.html', success=False, email_error=False, environment=environment))
    resp.mimetype = 'text/html'
    return resp

