#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime

from dateutil.parser import parse

from tweetid import db
from tweetid.models import Collection


def main():
    for collection in Collection.query.yield_per(1000):
        start_time = datetime.max
        end_time = datetime.min
        for tweet in collection.tweets.yield_per(1000):
            tweet_time = parse(tweet.created_at, ignoretz=True)
            db.session.expunge(tweet)
            start_time = min(start_time, tweet_time)
            end_time = max(end_time, tweet_time)

        start_iso = start_time.isoformat()
        end_iso = end_time.isoformat()
        print 'Start Time %s' % start_iso
        print 'End Time %s' % end_iso
        collection.first_tweet_date = start_iso
        collection.last_tweet_date = end_iso
        collection.save()
        print 'saved'


if __name__ == '__main__':
    main()