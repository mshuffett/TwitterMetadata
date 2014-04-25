# -*- coding: utf-8 -*-
from flask.ext.script import Manager

from tweetid import app, db


manager = Manager(app)


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
    """Create db tables."""
    db.drop_all()

manager.add_option('-c', '--config',
                   dest="config",
                   required=False,
                   help="config file")


if __name__ == "__main__":
    manager.run()
