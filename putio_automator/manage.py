#!/usr/bin/env python

import appdirs
import datetime
import distutils.dir_util
import json
import logging
import os
import pbr
import pbr.packaging
import pyinotify
import shutil
import sqlite3
import subprocess
import subprocess

try:
    import putiopy as putio
except ImportError:
    import putio

from app import create_app, init_db, APP_NAME, APP_AUTHOR
from flask import g
from flask_script import Manager, prompt
from json import load
from urllib2 import urlopen

app = create_app()

logging.basicConfig(filename=app.config.get('LOG_FILENAME'),
                    level=app.config.get('LOG_LEVEL', logging.WARNING),
                    format='%(asctime)s | %(levelname)-8s | %(name)-12s | %(message)s')

def sub_opts(app, **kwargs):
    pass

def define_db():
    manager = Manager(sub_opts, usage='Manage download database')

    @manager.command
    def forget(name):
        "Delete records of previous downloads in the database"
        with sqlite3.connect(app.config['DATABASE']) as connection:
            c = connection.cursor()
            c.execute('delete from downloads where name like ?', ('%%%s%%' % name,))
            print 'Affected rows: %s' % c.rowcount

    return manager

def define_torrents():
    manager = Manager(sub_opts, usage='Manage torrents')

    @manager.command
    def add(parent_id=0):
        "Add a torrent to the Put.io account"
        files = os.listdir(app.config['TORRENTS'])

        if len(files):
            with sqlite3.connect(app.config['DATABASE']) as connection:
                c = connection.cursor()

                for name in os.listdir(app.config['TORRENTS']):
                    path = os.path.join(app.config['TORRENTS'], name)
                    size = os.path.getsize(path)

                    c.execute("select datetime(created_at, 'localtime') from torrents where name = ? and size = ?", (name, size))
                    row = c.fetchone()

                    if row is None:
                        try:
                            app.logger.debug('adding torrent: %s' % path)
                            transfer = client.Transfer.add_torrent(path, parent_id=parent_id)
                            os.unlink(path)
                            app.logger.info('added transfer: %s' % transfer)
                        except Exception, e:
                            if e.message == 'BadRequest':
                                # Assume it's already added
                                os.unlink(path)
                                app.logger.warning('deleted torrent, already added : %s' % (name,))
                            else:
                                raise e

                        c.execute('insert into torrents (name, size) values (?, ?)', (name, size))
                        connection.commit()
                    else:
                        os.unlink(path)
                        app.logger.warning('deleted torrent, added at %s : %s' % (row[0], name))

    @manager.command
    def watch(add_existing=True, parent_id=0):
        "Watch a folder for new torrents to add to Put.io"
        torrents_add()

        class EventHandler(pyinotify.ProcessEvent):
            def process_IN_CLOSE_WRITE(self, event):
                app.logger.debug('adding torrent, received event: %s' % event)
                transfer = client.Transfer.add_torrent(event.pathname, parent_id=parent_id)
                os.unlink(event.pathname)
                app.logger.info('added transfer: %s' % transfer)

        wm = pyinotify.WatchManager()
        mask = pyinotify.IN_CLOSE_WRITE

        handler = EventHandler()
        notifier = pyinotify.Notifier(wm, handler)

        wdd = wm.add_watch(app.config['TORRENTS'], mask, rec=True)
        app.logger.debug('added watch: %s' % wdd)

        notifier.loop()

    return manager

def define_transfers():
    manager = Manager(sub_opts, usage='Manage transfers')

    @manager.command
    def cancel_by_status(statuses):
        "Cancel transfers by status"
        if isinstance(statuses, str):
            statuses = statuses.split(',')

        transfer_ids = []
        for transfer in client.Transfer.list():
            if transfer.status in statuses:
                transfer_ids.append(transfer.id)

        if len(transfer_ids):
            client.Transfer.cancel_multi(transfer_ids)

    @manager.command
    def cancel_completed():
        "Cancel completed transfers"
        transfers_cancel_by_status('COMPLETED')

    @manager.command
    def cancel_seeding():
        "Cancel seeding transfers"
        transfers_cancel_by_status('SEEDING')

    @manager.command
    def clean():
        "Clean finished transfers"
        client.Transfer.clean()

    @manager.command
    def groom():
        "Cancel seeding and completed transfers, and clean afterwards"
        transfers_cancel_by_status([ 'SEEDING', 'COMPLETED' ])
        transfers_clean()

    return manager

manager = Manager(app)
manager.add_command('db', define_db())
manager.add_command('torrents', define_torrents())
manager.add_command('transfers', define_transfers())

client = None

def init_client(c=None):
    global client

    if c is None:
        c = putio.Client(app.config['PUTIO_TOKEN'], use_retry=True)
    client = c
    return c

@manager.command
def supervisord():
    subprocess.call([
        'supervisord',
        '-n',
        '-c',
        '/etc/supervisor/supervisord.conf',
        '--logfile',
        '/dev/stdout',
        '--logfile_maxbytes',
        '0'
    ])

@manager.command
def init():
    dirs = appdirs.AppDirs(APP_NAME, APP_AUTHOR)

    incomplete = os.path.realpath(prompt('Incomplete directory', 'incomplete'))
    downloads = os.path.realpath(prompt('Downloads directory', 'downloads'))
    torrents = os.path.realpath(prompt('Torrents directory', 'torrents'))

    putio_token = prompt('OAuth Token')

    distutils.dir_util.mkpath(dirs.user_data_dir)

    config_path = os.path.realpath(prompt('Config file to write', os.path.join(dirs.user_data_dir, 'config.py')))

    with open(os.path.join(app.config['BASE_DIR'], 'config.py.dist'), 'r') as source:
        contents = (source.read()
            .replace("os.getenv('PUTIO_TOKEN')", "os.getenv('PUTIO_TOKEN', '" + putio_token + "')")
            .replace("/data/downloads", downloads)
            .replace("/data/incomplete", incomplete)
            .replace("/data/torrents", torrents))

        with open(config_path, 'w') as destination:
            destination.write(contents)

        os.chmod(config_path, 600)

def main():
    init_db(app)
    init_client()
    manager.run()

if __name__ == '__main__':
    main()
