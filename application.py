import ConfigParser
import logging
import os
import putio
import pyinotify
import sqlite3
import time

config = ConfigParser.ConfigParser()
config.read('application.ini')

settings = dict(config.items('settings'))

with sqlite3.connect(settings['database']) as connection:
    c = connection.cursor()

    c.execute('create table if not exists downloads (id integer primary key, name character varying, size integer, created_at timestamp default current_timestamp)')

    logging.basicConfig(filename=settings.get('log_filename', None), level=logging.DEBUG)

    client = putio.Client(settings['putio_token'])

    def download_files():
        for file in client.File.list():
            c.execute("select datetime(created_at, 'localtime') from downloads where name = ? and size = ?", (file.name, file.size))
            row = c.fetchone()

            if row is None:
                logging.debug('downloading file: %s' % file)
                file.download(dest=settings['downloads'], delete_after_download=True)
                logging.info('downloaded file: %s' % file)
                c.execute('insert into downloads (id, name, size) values (?, ?, ?)', (file.id, file.name, file.size))
            else:
                logging.warning('file downloaded at %s : %s' % (row[0], file))

    class EventHandler(pyinotify.ProcessEvent):
        def process_IN_CLOSE_WRITE(self, event):
            logging.debug('received event: %s' % event)
            transfer = client.Transfer.add_torrent(event.pathname)
            logging.info('transfer added: %s' % transfer)

    wm = pyinotify.WatchManager()
    mask = pyinotify.IN_CLOSE_WRITE

    handler = EventHandler()
    notifier = pyinotify.ThreadedNotifier(wm, handler)

    download_files()

    try:
        notifier.start()
        wdd = wm.add_watch(settings['torrents'], mask, rec=True)

        while True:
            time.sleep(float(settings.get('check_interval', 120)))
            download_files()
    finally:
        notifier.stop()
