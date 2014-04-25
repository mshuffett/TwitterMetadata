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

    def all(self):
        return self.query.all()


association_table = db.Table(
    'association',
    db.Column('collection_id', db.Integer, db.ForeignKey('collection.id')),
    db.Column('tweet_id', db.String, db.ForeignKey('tweet.id')))


class Tweet(ModelMixin, db.Model):
    id = db.Column(db.String, primary_key=True, index=True)
    created_at = db.Column(db.String)
    screen_name = db.Column(db.String)
    latitude = db.Column(db.String)
    longitude = db.Column(db.String)
    url_mentions = db.Column(db.String)

    # def __init__(self, id, text, created_at, screen_name, latitude, longitude, url_mentions=None):
    #     self.id = id
    #     self.text = text
    #     self.created_at = created_at
    #     self.screen_name = screen_name
    #     self.latitude = latitude
    #     self.longitude = longitude
    #     if url_mentions is not None:
    #         self.url_mentions = url_mentions

    def __repr__(self):
        return "<Tweet(id='%s')" % self.id


class Collection(ModelMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tweets = db.relationship('Tweet', secondary=association_table, lazy='dynamic',
                             backref=db.backref('collections', lazy='dynamic'))