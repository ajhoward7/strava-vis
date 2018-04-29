#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask, redirect, render_template, url_for, flash, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_login import (current_user, LoginManager, login_required,
                         login_user, logout_user, UserMixin)
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email
import os

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from plotly_example import plotly_map

from scrape import scrape_activities
from credentials import client_id, client_secret
import requests
import json

# Create and configure an app.
app = Flask(__name__)
bootstrap = Bootstrap(app)


@app.route('/login', methods=['GET', 'POST'])
def login():
    url = 'https://www.strava.com/oauth/authorize?response_type=code&redirect_uri=http%3A%2F%2F34.216.241.15%2Fauthorize&client_id=20812'
    return '<a href={}>Click here to authorise</a>'.format(url)


@app.route('/plotly_example', methods=('GET', 'POST'))
@login_required
def plotly_example():
    output = plotly_map()
    return render_template('plotly_map.html', source=output)


@app.route('/', methods=('GET', 'POST'))
def index():
    return render_template('index.html',
                           authenticated_user=current_user.is_authenticated)


@app.route('/authorize', methods=('GET','POST'))
def home():
    code = request.args.get('code')
    r = requests.post('https://www.strava.com/oauth/token', data={'client_id':client_id, 'client_secret':client_secret, 'code':code})
    access_token = json.loads(r.json()["access_token"])
    username = scrape_activities(access_token)

    return redirect('/{}'.format(username))

@app.route('/<username>', methods=('GET','POST'))
def load_activities(username):

    # Get activities from appropriate folder
    return "Here are some activities"



if __name__ == '__main__':

    app.run(host='0.0.0.0', port=80, debug=True)
