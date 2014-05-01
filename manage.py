# -*- coding: utf-8 -*-
import sys

from flask.ext.script import Manager

from tweetid import app, db
from tweetid.models import Collection
from tweetid.tsv import process_tsv


manager = Manager(app)


@manager.command
def load_tsv():
    """Load tsv"""
    # c = Collection(name='Queensland Floods', organization='QCRI', collection_type='keyword',
    #                keywords='#qldflood,#bigwet,queensland flood,australia flood, Missing, #qldfloods, #Bundaberg, queensland, #floods',
    #                year=2013, country='Australia')
    c = Collection(name='Oklahoma Tornado', organization='QCRI', collection_type='keyword',
                   keywords='oklahoma tornado, oklahoma storm, oklahoma relief, oklahoma volunteer, oklahoma disaster, #moore, moore relief, moore storm, moore tornado, moore flood, moore disaster, moore volunteer, #okc relief, #okc disaster, #okc tornado, #okc flood, #okc volunteer, #okc storm, #okwx, tornado, shawnee, norman, pottawatomie, mary fallin, #okc, #okneeds, #okhaves, #ok, #okhaves, #ok tornado, #ok relief, #ok flood, #ok disaster, #ok volunteer, #ok storm',
                   year=2013, country='US')
    process_tsv(sys.stdin, chunk_size=1000, collection=c)


@manager.command
def run():
    """Run in local machine."""
    app.run()


@manager.command
def init_db():
    """Create db tables."""
    db.create_all()


@manager.command
def drop_all():
    """Drop all db tables."""
    db.drop_all()


manager.add_option('-c', '--config',
                   dest="config",
                   required=False,
                   help="config file")

if __name__ == "__main__":
    manager.run()
