"""
Flask commands to manage torrents on Put.IO.
"""
import os
import pyinotify
import subprocess

from flask_script import Manager
from putio_automator.db import with_db
from putio_automator.manage import app


manager = Manager(usage='Manage torrents')

@manager.command
def add(parent_id=None):
    "Add a torrent"
    if parent_id == None:
        parent_id = app.config.get('PUTIO_ROOT', 0)
    files = os.listdir(app.config['TORRENTS'])

    if len(files):
        def func(connection):
            "Anonymous function"
            conn = connection.cursor()

            for name in os.listdir(app.config['TORRENTS']):
                path = os.path.join(app.config['TORRENTS'], name)
                size = os.path.getsize(path)

                conn.execute("select datetime(created_at, 'localtime') from torrents where name = ? and size = ?", (name, size))
                row = conn.fetchone()

                if row is None:
                    try:
                        app.logger.debug('adding torrent: %s' % path)
                        transfer = app.client.Transfer.add_torrent(path, parent_id=parent_id)
                        os.unlink(path)
                        app.logger.info('added transfer: %s' % transfer)
                    except Exception as e:
                        if e.message == 'BadRequest':
                            # Assume it's already added
                            os.unlink(path)
                            app.logger.warning('deleted torrent, already added : %s' % (name,))
                        else:
                            raise e

                    conn.execute('insert into torrents (name, size) values (?, ?)', (name, size))
                    connection.commit()
                else:
                    os.unlink(path)
                    app.logger.warning('deleted torrent, added at %s : %s' % (row[0], name))

        with_db(app, func)

@manager.command
def watch(parent_id=None, mount=False):
    "Watch a folder for new torrents to add"

    if parent_id == None:
        parent_id = app.config.get('PUTIO_ROOT', 0)
    if mount and not os.path.exists(app.config['TORRENTS']):
        subprocess.call([
            'mount',
            '-a'
        ])

    add()

    class EventHandler(pyinotify.ProcessEvent):
        "Event handler for responding to a new or updated torrent file"
        def process_IN_CLOSE_WRITE(self, event):
            "Do the above"
            app.logger.debug('adding torrent, received event: %s' % event)
            transfer = app.client.Transfer.add_torrent(event.pathname, parent_id=parent_id)
            os.unlink(event.pathname)
            app.logger.info('added transfer: %s' % transfer)

    watch_manager = pyinotify.WatchManager()
    mask = pyinotify.IN_CLOSE_WRITE

    handler = EventHandler()
    notifier = pyinotify.Notifier(watch_manager, handler)

    wdd = watch_manager.add_watch(app.config['TORRENTS'], mask, rec=True)
    app.logger.debug('added watch: %s' % wdd)

    notifier.loop()
