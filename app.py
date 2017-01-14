try:
    import putiopy as putio
except ImportError:
    import putio

import sqlite3

from flask import *

app = Flask(__name__)
app.config.from_object('config')

def init_db():
    with sqlite3.connect(app.config['DATABASE']) as connection:
        c = connection.cursor()

        c.execute('create table if not exists torrents (name character varying primary key, size integer, created_at timestamp default current_timestamp)')
        c.execute('create table if not exists downloads (id integer primary key, name character varying, size integer, created_at timestamp default current_timestamp)')
