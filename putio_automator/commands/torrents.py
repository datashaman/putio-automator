"""
Commands to manage torrents on Put.IO.
"""
import logging
logger = logging.getLogger(__name__)

import click
import os
import putiopy
import subprocess
import sys
import time

from putio_automator.cli import cli
from putio_automator.db import with_db

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


@cli.group()
def torrents():
    pass

@torrents.command()
@click.pass_context
@click.option('--parent-id', help='ID of folder to download from, defaults to root folder', type=int)
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
                if name[0] == '.':
                    continue

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
@click.option('--parent-id', help='ID of folder to download from, defaults to root folder', type=int)
@click.option('--mount', help='Mount all filesystems before watching', is_flag=True)
@click.option('--sleep', default=5, help='Amount of seconds to sleep between filesystem polls')
@click.option('--wait-for-closed', default=5, help='Amount of seconds to wait after created event to process a torrent')
def watch(ctx, parent_id=None, mount=False, sleep=5, wait_for_closed=5):
    "Watch a folder for new torrents to add"

    if parent_id is None:
        parent_id = ctx.obj['ROOT']

    if mount and not os.path.exists(ctx.obj['TORRENTS']):
        subprocess.call([
            'mount',
            '-a'
        ])

    ctx.invoke(add, parent_id=parent_id)

    class Handler(FileSystemEventHandler):
        # We cannot use on_closed because it is not supported
        # on MacOS's kqueue mechanism, so sleep for a few seconds
        # to allow the file to be written completely.
        def on_created(self, event):
            try:
                time.sleep(wait_for_closed)
                torrent_path = event.src_path
                ctx.obj['CLIENT'].Transfer.add_torrent(torrent_path, parent_id=parent_id)
                os.unlink(torrent_path)
                logger.debug('added torrent, on_created event for: %s' % torrent_path)
            except Exception as e:
                click.echo('error adding torrent: %s %s' % (torrent_path, e))
                logger.error('error adding torrent: %s %s' % (torrent_path, e))

    event_handler = Handler()
    observer = Observer()

    observer.schedule(event_handler, ctx.obj['TORRENTS'], recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(sleep)
    finally:
        observer.stop()
        observer.join()
