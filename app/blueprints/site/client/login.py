# encoding: utf-8
import os
import redis
from flask import Flask, render_template, make_response, request, redirect, session
from app.blueprints.site import SiteBlueprint

app = Flask(__name__)

@SiteBlueprint.route("/")
def index_login():
    if not session.get("name"):
        return redirect("/client/login")
    return render_template('client/login.html')

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
    session["name"] = request.form.get("name")
    print(session["name"])
    print(session)
    r = redis.Redis("localhost", 6379)
    for key in r.scan_iter():
        print(key)

 

    resp = make_response(render_template('client/login.html',
        success=False,
        errors=None,
        data_input=None))
    resp.mimetype = 'text/html'
    return resp

