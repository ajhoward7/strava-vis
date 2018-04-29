#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask, redirect, render_template, url_for, flash, request
from flask_bootstrap import Bootstrap
from plotly_plotting import process_activities

from scrape import scrape_activities
from credentials import client_id, client_secret
import requests
import json

# Create and configure an app.
app = Flask(__name__)
bootstrap = Bootstrap(app)


@app.route('/', methods=['GET', 'POST'])
def login():
    url = 'https://www.strava.com/oauth/authorize?response_type=code&redirect_uri=http%3A%2F%2F34.216.241.15%2Fauthorize&client_id=20812'
    return '<a href={}>Click here to authorise</a>'.format(url)


@app.route('/plotly_example', methods=('GET', 'POST'))
def plotly_example():
    output = plotly_map()
    return render_template('plotly_map.html', source=output)


@app.route('/authorize', methods=('GET','POST'))
def home():
    code = request.args.get('code')
    r = requests.post('https://www.strava.com/oauth/token', data={'client_id':client_id, 'client_secret':client_secret, 'code':code})
    json_data = json.loads(r._content)
    access_token = json_data["access_token"]
    username = scrape_activities(access_token)

    return redirect('/{}'.format(username))


@app.route('/<username>', methods=('GET','POST'))
def load_activities(username):

    output, output2, output3 = process_activities(username)
    return render_template('plotly_map.html', source=output, source2=output2, source3=output3)


if __name__ == '__main__':

    app.run(host='0.0.0.0', port=80, debug=True)
