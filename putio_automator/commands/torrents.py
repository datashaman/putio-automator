import os
import pyinotify

from flask_script import Manager
from putio_automator.db import with_db
from putio_automator.manage import app


manager = Manager(usage='Manage torrents')

@manager.command
def add(parent_id=0):
    "Add a torrent"
    files = os.listdir(app.config['TORRENTS'])

    if len(files):
        def func(connection):
            c = connection.cursor()

            for name in os.listdir(app.config['TORRENTS']):
                path = os.path.join(app.config['TORRENTS'], name)
                size = os.path.getsize(path)

                c.execute("select datetime(created_at, 'localtime') from torrents where name = ? and size = ?", (name, size))
                row = c.fetchone()

                if row is None:
                    try:
                        app.logger.debug('adding torrent: %s' % path)
                        transfer = app.client.Transfer.add_torrent(path, parent_id=parent_id)
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

        with_db(app, func)

@manager.command
def watch(add_existing=True, parent_id=0):
    "Watch a folder for new torrents to add"
    add()

    class EventHandler(pyinotify.ProcessEvent):
        def process_IN_CLOSE_WRITE(self, event):
            app.logger.debug('adding torrent, received event: %s' % event)
            transfer = app.client.Transfer.add_torrent(event.pathname, parent_id=parent_id)
            os.unlink(event.pathname)
            app.logger.info('added transfer: %s' % transfer)

    wm = pyinotify.WatchManager()
    mask = pyinotify.IN_CLOSE_WRITE

    handler = EventHandler()
    notifier = pyinotify.Notifier(wm, handler)

    wdd = wm.add_watch(app.config['TORRENTS'], mask, rec=True)
    app.logger.debug('added watch: %s' % wdd)

    notifier.loop()
