#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import tarfile

from models import Tweet, Collection
from tweetid import db


_TWEET_FIELDS = ('id', 'created_at', 'screen_name', 'latitude', 'longitude', 'url_mentions')


def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8', 'replace') for cell in row]


def process_tar(path, count=0):
    """
    Load the tar at path into database. If count is positive, limit number of tweets to load to count tweets.
    """
    tweets = []
    with tarfile.open(path, mode='r:gz') as tar:
        member = tar.getmembers()[0]  # assume single file tar
        f = tar.extractfile(member)
        tsv = csv.reader(f, delimiter='\t')
        for i, row in enumerate(tsv):
            if row[-1] != '\\N' or row[-2] != '\\N':
                print row
                raise Exception('Unexpected format.')
            row = row[:-2]

            tweets.append(Tweet(*row))

    oollection = Collection(tweets=tweets)
    collection.save()
    # print oollection.start_date, oollection.end_date


def tsv_tweet_gen(path, count=0):
    with open(path) as tsv_file:
        tsv = unicode_csv_reader(tsv_file, delimiter='\t')
        for i, row in enumerate(tsv):
            if row[-1] != '\\N' or row[-2] != '\\N':
                print row
                raise Exception('Unexpected format.')
            # row = row[:-2]

            kwargs = {}
            for i, field in enumerate(_TWEET_FIELDS):
                if row[i] != '\\N':
                    kwargs[field] = row[i]

            yield Tweet(**kwargs)
            count -= 1
            if count == 0:
                break


def process_tsv(path, count=0, chunk_size=0):
    """
    Load the tsv at path into database. If count is positive, limit number of tweets to load to count tweets.
    If chunk_size is positive chunk the saves by chunk_size amount.
    """
    collection = Collection()
    gen = tsv_tweet_gen(path, count=count)
    for i, tweet in enumerate(gen, 1):
        tweet.collections.append(collection)
        db.session.add(tweet)
        if chunk_size > 0 and i % chunk_size == 0:
            db.session.commit()

    db.session.commit()
    # print oollection.start_date, oollection.end_date

# process_tar('C:/Users/Michael/Downloads/twitterdata_oklahomatornado-20130520_20130530_GMT.tsv.tar.gz')
