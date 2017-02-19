import appdirs
import datetime
import distutils.dir_util
import os
import sqlite3

try:
    import putiopy as putio
except ImportError:
    import putio

from flask import Flask

APP_NAME = 'putio-automator'
APP_AUTHOR = 'datashaman'
APP_TAG = '%s/%s' % (APP_AUTHOR, APP_NAME)

from db import create_db, database_path

dirs = appdirs.AppDirs(APP_NAME, APP_AUTHOR)

def create_app(config=None):
    app = Flask(__name__)

    distutils.dir_util.mkpath(dirs.user_data_dir)

    if config is None:
        config = find_config()

    if config is not None:
        app.config.from_pyfile(config)

    create_db(app)
    app.client = create_client(app)

    return app

def create_client(app):
    if 'PUTIO_TOKEN' in app.config:
        client = putio.Client(app.config['PUTIO_TOKEN'], use_retry=True)

        return client

def date_handler(obj):
    if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
        return obj.isoformat()
    else:
        return None

def find_config():
    search_paths = [
        os.path.join(os.getcwd(), 'config.py'),
        os.path.join(dirs.user_data_dir, 'config.py'),
        os.path.join(dirs.site_data_dir, 'config.py'),
    ]

    config = None

    for search_path in search_paths:
        if os.path.exists(search_path) and not os.path.isdir(search_path):
            config = search_path
            break

    return config
