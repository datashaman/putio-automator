try:
    import putiopy as putio
except ImportError:
    import putio

import appdirs
import os
import sqlite3

from flask import *

APP_NAME = 'putio_automator'
APP_AUTHOR = 'datashaman'

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

    return app

def init_db(app):
    with sqlite3.connect(app.config['DATABASE']) as connection:
        c = connection.cursor()

        c.execute('create table if not exists torrents (name character varying primary key, size integer, created_at timestamp default current_timestamp)')
        c.execute('create table if not exists downloads (id integer primary key, name character varying, size integer, created_at timestamp default current_timestamp)')
