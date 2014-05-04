#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declared_attr

from tweetid.app import db


class ModelMixin(object):
    """
    This is a base class with delivers all basic database operations
    """

    @declared_attr
    def __tablename__(cls):
        """Get table name from class name"""
        return cls.__name__.lower()

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def save_multiple(objects=[]):
        db.session.add_all(objects)
        db.session.commit()

    @staticmethod
    def update():
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def all(cls):
        return cls.query.all()


association_table = db.Table(
    'association',
    db.Column('collection_name', db.Integer, db.ForeignKey('collection.name')),
    db.Column('tweet_id', db.String, db.ForeignKey('tweet.id')))


class Tweet(ModelMixin, db.Model):
    id = db.Column(db.String, primary_key=True, index=True)
    created_at = db.Column(db.String)
    screen_name = db.Column(db.String)
    latitude = db.Column(db.String)
    longitude = db.Column(db.String)
    url_mentions = db.Column(db.String)

    @property
    def serialize(self):
        """Return object in easily serializable format."""
        return {
            'twitter': {
                'id_str': self.id,
                'created_at': self.created_at,
                'screen_name': self.screen_name,
                'coordinates': {
                    'coordinates': [float(self.longitude), float(self.latitude)],
                    'type': 'Point'},
                'entities': {
                    'urls': [{'expanded_url': mention for mention in self.url_mentions.split(' ')}]
                }
            },
            'tweetid': {
                'collections': [collection.name for collection in self.collections]
            }
        }

    def __repr__(self):
        return "<Tweet(id='%s')>" % self.id


class Collection(ModelMixin, db.Model):
    name = db.Column(db.String, primary_key=True, index=True)
    organization = db.Column(db.String, index=True)
    description = db.Column(db.String)
    collection_type = db.Column(db.String)
    keywords = db.Column(db.String)
    country = db.Column(db.String)
    year = db.Column(db.Integer)
    tags = db.Column(db.String)
    tweets = db.relationship('Tweet', secondary=association_table, lazy='dynamic',
                             backref=db.backref('collections', lazy='dynamic'))

    def __repr__(self):
        return "<Collection(name='%s')>" % self.name
