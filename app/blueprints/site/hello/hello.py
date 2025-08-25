import re
import os 
import base64
from flask import Flask, render_template, make_response, send_file, request, jsonify
from app.blueprints.site import SiteBlueprint
from os.path import join, dirname, realpath
from werkzeug.utils import secure_filename

from app import logging
from app import environment


@SiteBlueprint.route('/hello/hello', methods=['GET'])
def hellos():
    return 'Hello, World!'
