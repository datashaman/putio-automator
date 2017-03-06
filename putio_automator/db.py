import appdirs
import os
import sqlite3

from putio_automator import APP_NAME, APP_AUTHOR


database_path = os.path.join(appdirs.user_data_dir(APP_NAME, APP_AUTHOR), 'downloads.db')

def with_db(app, func):
    if not os.path.exists(database_path):
        open(database_path, 'w').close()

    with sqlite3.connect(database_path) as connection:
        func(connection)

def create_db(app):
    def func(connection):
        c = connection.cursor()
        c.execute('create table if not exists torrents (name character varying primary key, size integer, created_at timestamp default current_timestamp)')
        c.execute('create table if not exists downloads (id integer primary key, name character varying, size integer, created_at timestamp default current_timestamp)')
    with_db(app, func)
