"""
Initialize the application.
"""
import datetime
import distutils.dir_util
import os
import sqlite3

try:
    import putiopy as putio
except ImportError:
    import putio

from flask import Flask

import appdirs

APP_NAME = 'putio-automator'
APP_AUTHOR = 'datashaman'
APP_TAG = '%s/%s' % (APP_AUTHOR, APP_NAME)

from db import create_db, database_path

DIRS = appdirs.AppDirs(APP_NAME, APP_AUTHOR)

def create_app(config=None):
    "Create a Flask app given config"
    app = Flask(__name__)

    distutils.dir_util.mkpath(DIRS.user_data_dir)

    if config is None:
        config = find_config()

    if config is not None:
        app.config.from_pyfile(config)

    create_db(app)
    app.client = create_client(app)

    return app

def create_client(app):
    "Create a Put.IO client"
    if 'PUTIO_TOKEN' in app.config:
        client = putio.Client(app.config['PUTIO_TOKEN'], use_retry=True)

        return client

def date_handler(obj):
    "Date handler for JSON serialization"
    if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
        return obj.isoformat()
    else:
        return None

def find_config(verbose=False):
    "Search for config on wellknown paths"
    search_paths = [
        os.path.join(os.getcwd(), 'config.py'),
        os.path.join(DIRS.user_data_dir, 'config.py'),
        os.path.join(DIRS.site_data_dir, 'config.py'),
    ]

    config = None

    for search_path in search_paths:
        if verbose:
            print("Searching %s" % search_path)

        if os.path.exists(search_path) and not os.path.isdir(search_path):
            config = search_path
            break

    return config
