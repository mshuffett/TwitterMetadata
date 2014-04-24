#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
Bootstrap(app)

app.config['SECRET_KEY'] = 'devkey'
app.config['RECAPTCHA_PUBLIC_KEY'] = \
    '6Lfol9cSAAAAADAkodaYl9wvQCwBMr3qGR_PPHcw'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tweetid.db'
db = SQLAlchemy(app)

import tweetid.models as models
from tweetid.tsv import process_tsv

@app.route('/', methods=['GET', 'POST'])
def index():
    tweet = models.Tweet.query.first()
    return render_template('index.html', tweet=tweet)
