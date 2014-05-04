#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict
import json
import os

from flask import Flask, render_template, request, flash, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from config import DefaultConfig, INSTANCE_FOLDER_PATH
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap
from wtforms import TextField, TextAreaField, SubmitField, SelectField
from flask_wtf import Form
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired


__all__ = ['app', 'db']

DEFAULT_BLUEPRINTS = ()


def create_app(config=None, app_name=None, blueprints=None):
    """Create a Flask app."""

    if app_name is None:
        app_name = DefaultConfig.PROJECT
    if blueprints is None:
        blueprints = DEFAULT_BLUEPRINTS

    app = Flask(app_name, instance_path=INSTANCE_FOLDER_PATH, instance_relative_config=True)
    configure_app(app, config)
    configure_blueprints(app, blueprints)
    configure_extensions(app)
    configure_logging(app)

    return app


def configure_app(app, config=None):
    """Different ways of configurations."""

    # http://flask.pocoo.org/docs/api/#configuration
    app.config.from_object(DefaultConfig)

    # http://flask.pocoo.org/docs/config/#instance-folders
    app.config.from_pyfile('production.cfg', silent=True)

    if config:
        app.config.from_object(config)

        # Use instance folder instead of env variables to make deployment easier.
        #app.config.from_envvar('%s_APP_CONFIG' % DefaultConfig.PROJECT.upper(), silent=True)


def configure_extensions(app):
    Bootstrap(app)


def configure_blueprints(app, blueprints):
    """Configure blueprints in views."""

    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def configure_logging(app):
    """Configure file(info) and email(error) logging."""

    if app.debug or app.testing:
        # Skip debug and test mode. Just check standard output.
        return

    import logging

    # Set info level on logger, which might be overwritten by handers.
    # Suppress DEBUG messages.
    app.logger.setLevel(logging.INFO)

    info_log = os.path.join(app.config['LOG_FOLDER'], 'info.log')
    info_file_handler = logging.handlers.RotatingFileHandler(info_log, maxBytes=100000, backupCount=10)
    info_file_handler.setLevel(logging.INFO)
    info_file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]')
    )
    app.logger.addHandler(info_file_handler)

    # Testing
    #app.logger.info("testing info.")
    #app.logger.warn("testing warn.")
    #app.logger.error("testing error.")


app = create_app()
db = SQLAlchemy(app)
from tweetid.models import Collection, Tweet
import tsv


class UploadForm(Form):
    name = TextField('Collection Name', validators=[DataRequired()])
    organization = TextField('Organization')
    description = TextAreaField('Description', validators=[DataRequired()])
    collection_type = SelectField('Collection Type', choices=[('keyword', 'Keyword Based')])
    keywords = TextAreaField('Keywords')
    country = TextField('Country')
    year = TextField('Year')
    tags = TextField('Tags')
    collection_file = FileField('Collection File',
                                description="""Currently expects a tsv file with no headers with the fields:
                                id, created_at, screen_name, latitude, longitude, url_mentions.
                                See the <a href="http://dev.twitter.com/docs/platform-objects/tweets">
                                Twitter Documentation</a> for descriptions of these fields.""",
                                validators=[FileRequired(),
                                            FileAllowed(['txt', 'csv', 'tsv', 'json'],
                                                        'Text only!')])
    submit_button = SubmitField('Submit Form')


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/collections', methods=['GET', 'POST'])
def collections():
    collections = Collection.query.order_by(Collection.organization)
    org_d = defaultdict(list)
    for c in collections:
        org_d[c.organization].append(c)
    return render_template('collections.html', org_d=org_d)


@app.route('/collection/<name>', methods=['GET', 'POST'])
def collection(name):
    c = Collection.query.get_or_404(name)
    page = request.args.get('page', 1)
    tweets = c.tweets.paginate(int(page))
    return render_template('collection_details.html', collection=c, tweets=tweets)


@app.route('/tweets', methods=['GET', 'POST'])
def tweets():
    page = request.args.get('page', 1)
    app.logger.info('Tweets page %s' % page)
    tweets = Tweet.query.paginate(int(page))
    app.logger.info('Pagination page %s' % tweets.page)
    return render_template('tweets.html', tweets=tweets)


@app.route('/tweets/<tweet_id>', methods=['GET', 'POST'])
def tweet(tweet_id):
    tweet = Tweet.query.get(tweet_id)
    return render_template('single_tweet.html', tweet=tweet, tweet_json=json.dumps(tweet.serialize, indent=4))


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        data = form.collection_file.data
        collection = Collection()
        collection.name = form.name.data
        collection.organization = form.organization.data
        collection.description = form.description.data
        collection.collection_type = form.collection_type.data
        collection.keywords = form.keywords.data
        collection.country = form.country.data
        collection.year = form.year.data
        collection.tags = form.tags.data
        # filename = secure_filename(data.filename)
        # file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        # data.save(file_path)
        tsv.process_tsv(data, chunk_size=1000, collection=collection)
        flash('The collection was saved successfully.')
    return render_template('upload.html', form=form)


@app.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template('contact.html')


@app.route('/merge', methods=['GET', 'POST'])
def merge():
    return render_template('merge.html')


@app.route('/do_merge', methods=['POST'])
def do_merge():
    app.logger.info('Merging')
    c1 = Collection.query.get(request.form['c1'])
    c2 = Collection.query.get(request.form['c2'])
    tweets = c1.tweets.union(c2.tweets).paginate(1)
    keywords = {k.strip() for k in c1.keywords.split(',')}
    keywords.update(k.strip() for k in c2.keywords.split(','))
    return render_template('completed_merge.html', c1=c1, c2=c2, tweets=tweets, keywords=', '.join(keywords))
