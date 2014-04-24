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


class ModelMixin(object):
    '''
    This is a baseclass with delivers all basic database operations
    '''

    @declared_attr
    def __tablename__(cls):
        '''Get table name from class name'''
        return cls.__name__.lower()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def save_multiple(self, objects = []):
        db.session.add_all(objects)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def query_object(self):
        return db.session.query(self.__class__)

    def all(self):
        return self.queryObject().all()


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')
