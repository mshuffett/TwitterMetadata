# -*- coding: utf-8 -*-

import os

from utils import make_dir


INSTANCE_FOLDER_PATH = os.path.join('C:/Users/Michael/AppData/Local/Temp/', 'instance')


class BaseConfig(object):
    PROJECT = "TweetID"

    DEBUG = False
    TESTING = False

    LOG_FOLDER = INSTANCE_FOLDER_PATH + '/logs'
    make_dir(LOG_FOLDER)


class DefaultConfig(BaseConfig):
    DEBUG = True
    UPLOAD_FOLDER = 'C:/Users/Michael/Dropbox/ws/TwitterMetadata/uploads'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///tweetid.db'


class TestConfig(BaseConfig):
    TESTING = True

