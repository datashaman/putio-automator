import appdirs
import os
import pathlib
import sqlite3

from putio_automator import APP_NAME, APP_AUTHOR


user_data_dir = appdirs.user_data_dir(APP_NAME, APP_AUTHOR)
database_path = os.path.join(user_data_dir, 'downloads.db')

def with_db(func):
    if not os.path.exists(database_path):
        pathlib.Path(user_data_dir).mkdir(parents=True, exist_ok=True)
        open(database_path, 'w').close()

    with sqlite3.connect(database_path) as connection:
        func(connection)

def create_db():
    def func(connection):
        c = connection.cursor()
        c.execute('create table if not exists torrents (name character varying primary key, size integer, created_at timestamp default current_timestamp)')
        c.execute('create table if not exists downloads (id integer primary key, name character varying, size integer, created_at timestamp default current_timestamp)')
    with_db(func)
