#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_appconfig import AppConfig
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker
import datetime

Base = declarative_base()


class Singleton(object):
    '''
    Singelton class
    '''
    def __init__(self, decorated):
        self._decorated = decorated

    def instance(self, *args, **kwargs):
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated(*args, **kwargs)
            return self._instance

    def __call__(self, *args, **kwargs):
        raise TypeError('Singletons must be accessed through the `Instance` method.')


@Singleton
class Db(object):
    '''
    The DB Class should only exits once, thats why it has the @Singleton decorator.
    To Create an instance you have to use the instance method:
        db = Db.instance()
    '''
    engine = None
    session = None

    def __init__(self):
        self.engine = create_engine('sqlite:///showpy.db', echo=True)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        ## Create all Tables
        Base.metadata.create_all(self.engine)

    def instance(self, *args, **kwargs):
        '''
        Dummy method, cause several IDEs can not handel singeltons in Python
        '''
        pass


class ModelMixin(object):
    '''
    This is a baseclass with delivers all basic database operations
    '''

    @declared_attr
    def __tablename__(cls):
        '''Get table name from class name'''
        return cls.__name__.lower()

    def save(self):
        db = Db.instance()
        db.session.add(self)
        db.session.commit()

    def save_multiple(self, objects = []):
        db = Db.instance()
        db.session.add_all(objects)
        db.session.commit()

    def update(self):
        db = Db.instance()
        db.session.commit()

    def delete(self):
        db = Db.instance()
        db.session.delete(self)
        db.session.commit()

    def query_object(self):
        db = Db.instance()
        return db.session.query(self.__class__)

    def all(self):
        return self.queryObject().all()


class Show(ModelMixin, Base):
    title = Column(String, primary_key=True)

    def __repr__(self):
        return "<Show(title='%s')>" % self.title

def create_app(configfile=None):
    app = Flask(__name__)
    AppConfig(app, configfile)  # Flask-Appconfig is not necessary, but
                                # highly recommend =)
                                # https://github.com/mbr/flask-appconfig
    Bootstrap(app)

    # in a real app, these should be configured through Flask-Appconfig
    app.config['SECRET_KEY'] = 'devkey'
    app.config['RECAPTCHA_PUBLIC_KEY'] = \
        '6Lfol9cSAAAAADAkodaYl9wvQCwBMr3qGR_PPHcw'

    @app.route('/', methods=['GET', 'POST'])
    def index():
        return render_template('index.html')

    return app

if __name__ == '__main__':
    app = create_app().run(debug=True)
