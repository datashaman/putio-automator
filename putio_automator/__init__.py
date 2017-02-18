import appdirs
import datetime
import os
import sqlite3

try:
    import putiopy as putio
except ImportError:
    import putio

from flask import Flask

APP_NAME = 'putio_automator'
APP_AUTHOR = 'datashaman'

def create_db(app):
    with sqlite3.connect(app.config['DATABASE']) as connection:
        c = connection.cursor()
        c.execute('create table if not exists torrents (name character varying primary key, size integer, created_at timestamp default current_timestamp)')
        c.execute('create table if not exists downloads (id integer primary key, name character varying, size integer, created_at timestamp default current_timestamp)')

def create_app(config=None):
    app = Flask(__name__)

    dirs = appdirs.AppDirs(APP_NAME, APP_AUTHOR)

    if config is None:
        search_paths = [
            os.path.join(os.getcwd(), 'config.py'),
            os.path.join(dirs.user_data_dir, 'config.py'),
            os.path.join(dirs.site_data_dir, 'config.py'),
        ]

        for search_path in search_paths:
            if os.path.exists(search_path) and not os.path.isdir(search_path):
                config = search_path
                break

    app.config.from_pyfile(config)

    create_db(app)
    app.client = create_client(app)

    return app

def create_client(app):
    client = putio.Client(app.config['PUTIO_TOKEN'], use_retry=True)

    return client

def date_handler(obj):
    if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
        return obj.isoformat()
    else:
        return None
