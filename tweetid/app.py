#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from collections import namedtuple
import os

from flask import Flask, render_template, request
from flask.ext.migrate import Migrate
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
import tweetid.models as models

Collection = namedtuple('Collection', ['name', 'description'])


class UploadForm(Form):
    title = TextField('Title', validators=[DataRequired()])
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
    tweet = models.Tweet.query.first()
    c = Collection('name', 'description')
    collections = [c for x in xrange(10)]
    return render_template('index.html', tweet=tweet, collections=collections)


@app.route('/collections', methods=['GET', 'POST'])
def collections():
    c = Collection('name', 'description')
    collections = [c for x in xrange(10)]
    return render_template('collections.html', collections=collections)


@app.route('/tweets', methods=['GET', 'POST'])
def tweets():
    page = request.args.get('page', 1)
    app.logger.info('Tweets page %s' % page)
    tweet = models.Tweet.query.first()
    tweets = models.Tweet.query.paginate(int(page))
    app.logger.info('Pagination page %s' % tweets.page)
    return render_template('tweets.html', tweet=tweet, tweets=tweets)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        data = form.collection_file.data
        filename = secure_filename(data.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        data.save(file_path)

    else:
        filename = None
    return render_template('upload.html', form=form, filename=filename)


@app.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template('contact.html')
