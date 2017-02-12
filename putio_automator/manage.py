#!/usr/bin/env python

import appdirs
import datetime
import json
import logging
import os
import pbr
import pbr.packaging
import subprocess

try:
    import putiopy as putio
except ImportError:
    import putio

import distutils.dir_util
import pyinotify
import shutil
import sqlite3
import subprocess

from app import create_app, init_db, APP_NAME, APP_AUTHOR
from json import load
from urllib2 import urlopen
from flask import g
from flask_script import Manager, prompt

app = create_app()

logging.basicConfig(filename=app.config.get('LOG_FILENAME'),
                    level=app.config.get('LOG_LEVEL', logging.WARNING),
                    format='%(asctime)s | %(levelname)-8s | %(name)-12s | %(message)s')

def date_handler(obj):
    if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
        return obj.isoformat()
    else:
        return None

client = None

def init_client(c=None):
    global client

    if c is None:
        c = putio.Client(app.config['PUTIO_TOKEN'], use_retry=True)
    client = c
    return c

manager = Manager(app)
# manager.add_option('-c', '--config', dest='config', required=False)

@manager.command
def transfers_cancel_by_status(statuses):
    if isinstance(statuses, str):
        statuses = statuses.split(',')

    transfer_ids = []
    for transfer in client.Transfer.list():
        if transfer.status in statuses:
            transfer_ids.append(transfer.id)

    if len(transfer_ids):
        client.Transfer.cancel_multi(transfer_ids)

@manager.command
def transfers_cancel_seeding():
    transfers_cancel_by_status('SEEDING')

@manager.command
def transfers_cancel_completed():
    transfers_cancel_by_status('COMPLETED')

@manager.command
def transfers_clean():
    client.Transfer.clean()

@manager.command
def transfers_groom():
    transfers_cancel_by_status([ 'SEEDING', 'COMPLETED' ])
    transfers_clean()

@manager.command
def torrents_add(parent_id=0):
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
def torrents_watch(add_existing=True, parent_id=0):
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

@manager.command
def files_list(parent_id=0):
    files = client.File.list(parent_id)
    print json.dumps([vars(f) for f in files], indent=4, default=date_handler)

@manager.command
def files_download(limit=None, chunk_size=256, parent_id=0):
    files = client.File.list(parent_id)
    app.logger.info('%s files found' % len(files))

    if len(files):
        with sqlite3.connect(app.config['DATABASE']) as connection:
            if limit is not None:
                downloaded = 0

            c = connection.cursor()

            for f in files:
                c.execute("select datetime(created_at, 'localtime') from downloads where name = ? and size = ?", (f.name, f.size))
                row = c.fetchone()

                if row is None:
                    app.logger.debug('downloading file: %s' % f)
                    f.download(dest=app.config['INCOMPLETE'], delete_after_download=True, chunk_size=int(chunk_size)*1024)
                    app.logger.info('downloaded file: %s' % f)

                    path = os.path.join(app.config['INCOMPLETE'], f.name)
                    shutil.move(path, app.config['DOWNLOADS'])

                    c.execute('insert into downloads (id, name, size) values (?, ?, ?)', (f.id, f.name, f.size))
                    connection.commit()

                    if limit is not None:
                        downloaded = downloaded + 1

                        if downloaded > limit:
                            break
                else:
                    app.logger.warning('file already downloaded at %s : %s' % (row[0], f))

@manager.command
def forget(name):
    with sqlite3.connect(app.config['DATABASE']) as connection:
        c = connection.cursor()
        c.execute('delete from downloads where name like ?', ('%%%s%%' % name,))
        print 'Affected rows: %s' % c.rowcount

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

def main():
    init_db(app)
    init_client()
    manager.run()

if __name__ == '__main__':
    main()
