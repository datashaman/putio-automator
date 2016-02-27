#!/usr/bin/env python

import datetime
import json
import logging
import os
import putio
import pyinotify
import shutil
import sqlite3

from flask import g
from flask.ext.hookserver import Hooks
from flask.ext.script import Manager

from app import app, init_db

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

hooks = Hooks(app, url='/hooks')

@hooks.hook('ping')
def ping(data, guid):
    print data, guid
    return 'pong'

manager = Manager(app)

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
def torrents_add():
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
                        transfer = client.Transfer.add_torrent(path)
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
def torrents_watch(add_existing=True):
    torrents_add()

    class EventHandler(pyinotify.ProcessEvent):
        def process_IN_CLOSE_WRITE(self, event):
            app.logger.debug('adding torrent, received event: %s' % event)
            transfer = client.Transfer.add_torrent(event.pathname)
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
def files_list():
    files = client.File.list()
    print json.dumps([vars(f) for f in files], indent=4, default=date_handler)

@manager.command
def files_download(limit=None, chunk_size=256):
    files = client.File.list()
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

if __name__ == '__main__':
    init_db()
    init_client()
    manager.run()
