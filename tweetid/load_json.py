#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import time

from sqlalchemy.exc import IntegrityError

from tweetid import db
from tweetid.models import Collection, Tweet


def _tweet_gen(collection_json, collection):
    for tweet_json in collection_json.get('tweets', []):
        tweet = Tweet.query.get(tweet_json['id'])
        if tweet is None:
            # Tweet didn't exist in database
            tweet = Tweet(id=tweet_json['id'],
                          created_at=tweet_json.get('created_at'),
                          screen_name=tweet_json.get('from_user'),
                          latitude=tweet_json.get('geo_coordinates_0'),
                          longitude=tweet_json.get('geo_coordinates_1'))

        tweet.collections.append(collection)
        yield tweet


def load_json(fp, collection_name, organization='Virginia Tech', country='US', chunk_size=1000):
    """Loads json file exported from YourTwapperKepper with file pointer fp into database"""
    j = json.load(fp)
    collection_info = j.get('archive_info', {})

    created_time = collection_info.get('create_time')
    if created_time:
        year = time.gmtime(float(created_time)).tm_year
    else:
        year = None

    collection = Collection(name=collection_name,
                            organization=organization,
                            description=collection_info.get('description'),
                            collection_type='keyword',
                            keywords=collection_info.get('keyword'),
                            country=country,
                            year=year,
                            tags=collection_info.get('tags'))

    error_count = 0
    for i, tweet in enumerate(_tweet_gen(j, collection), start=1):
        db.session.add(tweet)

        if chunk_size > 0 and i % chunk_size == 0:
            try:
                db.session.commit()
            except IntegrityError as e:
                error_count += 1
                print 'Error %s' % error_count

            print 'First %s done' % ((i + 1) * chunk_size)

    db.session.add(collection)
    db.session.commit()