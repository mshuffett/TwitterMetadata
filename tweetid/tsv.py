#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv

import tarfile

from models import Tweet, Collection
from tweetid.app import db, app


_TWEET_FIELDS = ('id', 'text', 'created_at', 'screen_name', 'latitude', 'longitude', 'url_mentions')


def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8', 'replace') for cell in row]


def tsv_tweet_gen(fp, count=0):
    tsv = unicode_csv_reader(fp, delimiter='\t', quotechar='\x07')
    for i, row in enumerate(tsv):
        assert len(row) == 9
        if row[-1] != '\\N' or row[-2] != '\\N':
            print row
            app.logger.error('Unexpected format.\n%s\n%s\t%s' % (row, row[-1], row[-2]))
            raise Exception('Unexpected format.')
        row = row[:-2]

        kwargs = {}
        for i, field in enumerate(_TWEET_FIELDS):
            if row[i] == '\\N' or field == 'text':
                continue
            kwargs[field] = row[i]

        yield Tweet(**kwargs)
        count -= 1
        if count == 0:
            break


def process_tsv(fp, count=0, chunk_size=0, collection=None):
    """
    Load the tsv at path into database. If count is positive, limit number of tweets to load to count tweets.
    If chunk_size is positive chunk the saves by chunk_size amount.
    """
    if collection is None:
        collection = Collection()
    gen = tsv_tweet_gen(fp, count=count)
    for i, tweet in enumerate(gen, 1):
        existing_tweet = Tweet.query.get(tweet.id)
        if existing_tweet is None:
            tweet.collections.append(collection)
            db.session.add(tweet)
        else:
            existing_tweet.collections.append(collection)
            db.session.add(existing_tweet)
        if chunk_size > 0 and i % chunk_size == 0:
            db.session.commit()

    db.session.commit()
    # print oollection.start_date, oollection.end_date

# process_tar('C:/Users/Michael/Downloads/twitterdata_oklahomatornado-20130520_20130530_GMT.tsv.tar.gz')
