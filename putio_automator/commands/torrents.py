"""
Flask commands to manage torrents on Put.IO.
"""
import logging
logger = logging.getLogger(__name__)

import click
import os
import putiopy
import subprocess

from fswatch import Monitor
from putio_automator.cli import cli
from putio_automator.db import with_db


@cli.group()
def torrents():
    pass

@torrents.command()
@click.pass_context
def add(ctx, parent_id=None):
    "Add a torrent"
    if parent_id == None:
        parent_id = ctx.obj['ROOT']
    folder = ctx.obj['TORRENTS']
    files = os.listdir(folder)
    files = list(f for f in files if os.path.isfile(os.path.join(folder, f)))

    if len(files):
        def func(connection):
            "Anonymous function"
            conn = connection.cursor()

            for name in files:
                path = os.path.join(folder, name)
                size = os.path.getsize(path)

                conn.execute("select datetime(created_at, 'localtime') from torrents where name = ? and size = ?", (name, size))
                row = conn.fetchone()

                if row is None:
                    try:
                        logger.debug('adding torrent: %s' % path)
                        transfer = ctx.obj['CLIENT'].Transfer.add_torrent(path, parent_id=parent_id)
                        os.unlink(path)
                        logger.info('added transfer: %s - %s' % (transfer.id, name))
                    except:
                        info = sys.exc_info()

                        if info[0] == putiopy.ClientError and info[1].type == 'UnknownError':
                            # Assume it's already added
                            os.unlink(path)
                            logger.warning('deleted torrent, already added : %s' % (name,))
                        else:
                            raise

                    conn.execute('insert into torrents (name, size) values (?, ?)', (name, size))
                    connection.commit()
                else:
                    os.unlink(path)
                    logger.warning('deleted torrent, added at %s : %s' % (row[0], name))

        with_db(func)

@torrents.command()
@click.pass_context
def watch(ctx, parent_id=None, mount=False):
    "Watch a folder for new torrents to add"

    if parent_id is None:
        parent_id = ctx.obj['ROOT']

    if mount and not os.path.exists(ctx.obj['TORRENTS']):
        subprocess.call([
            'mount',
            '-a'
        ])

    ctx.invoke(add, parent_id=parent_id)

    monitor = Monitor()
    monitor.add_path(ctx.obj['TORRENTS'])

    def callback(path, evt_time, flags, flags_num, event_num):
        torrent_path = path.decode()
        logger.debug('adding torrent, received event for: %s' % torrent_path)
        transfer = ctx.obj['CLIENT'].Transfer.add_torrent(path.decode(), parent_id=parent_id)
        os.unlink(torrent_path)
        logger.info('added transfer: %s' % transfer)

    monitor.set_callback(callback)
    monitor.start()
