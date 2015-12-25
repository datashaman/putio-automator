import ConfigParser
import logging
import os
import putio
import pyinotify
import sqlite3
import time
import shutil

config = ConfigParser.ConfigParser()
config.read('application.ini')

settings = dict(config.items('settings'))

with sqlite3.connect(settings['database']) as connection:
    c = connection.cursor()

    c.execute('create table if not exists torrents (name character varying primary key, size integer, created_at timestamp default current_timestamp)')
    c.execute('create table if not exists downloads (id integer primary key, name character varying, size integer, created_at timestamp default current_timestamp)')

    logging.basicConfig(filename=settings.get('log_filename', None), level=logging.DEBUG)

    client = putio.Client(settings['putio_token'])

    clean_interval = float(settings.get('clean_interval', 10))
    download_interval = float(settings.get('download_interval', 120))

    def download_files():
        files = client.File.list()

        downloaded = 0
        download_limit = settings.get('download_limit')

        for file in files:
            c.execute("select datetime(created_at, 'localtime') from downloads where name = ? and size = ?", (file.name, file.size))
            row = c.fetchone()

            if row is None:
                logging.debug('downloading file: %s' % file)
                file.download(dest=settings['incomplete'], delete_after_download=True)
                logging.info('downloaded file: %s' % file)

                path = os.path.join(settings['incomplete'], file.name)
                shutil.move(path, settings['downloads'])

                c.execute('insert into downloads (id, name, size) values (?, ?, ?)', (file.id, file.name, file.size))
                connection.commit()

                if download_limit is not None:
                    downloaded = downloaded + 1

                    if downloaded > download_limit:
                        break
            else:
                logging.warning('file downloaded at %s : %s' % (row[0], file))

    def clean_transfers():
        transfer_ids = []
        for transfer in client.Transfer.list():
            if transfer.status == 'SEEDING':
                transfer_ids.append(transfer.id)

        if len(transfer_ids):
            client.Transfer.cancel(transfer_ids)

        client.Transfer.clean()

    def add_torrents():
        for name in os.listdir(settings['torrents']):
            path = os.path.join(settings['torrents'], name)
            size = os.path.getsize(path)

            c.execute("select datetime(created_at, 'localtime') from torrents where name = ? and size = ?", (name, size))
            row = c.fetchone()

            if row is None:
                logging.debug('adding torrent: %s' % name)

                try:
                    logging.info('adding torrent: %s' % path)
                    transfer = client.Transfer.add_torrent(path)
                    logging.info('added torrent: %s' % transfer)
                except Exception, e:
                    if e.message == 'BadRequest':
                        # Assume it's already added
                        os.unlink(path)
                        logging.warning('deleted torrent, already added : %s' % (name,))
                    else:
                        raise e

                c.execute('insert into torrents (name, size) values (?, ?)', (name, size))
                connection.commit()
            else:
                os.unlink(path)
                logging.warning('deleted torrent, added at %s : %s' % (row[0], name))

    def watch_torrents():
        class EventHandler(pyinotify.ProcessEvent):
            def process_IN_CLOSE_WRITE(self, event):
                logging.debug('received event: %s' % event)
                transfer = client.Transfer.add_torrent(event.pathname)
                logging.info('transfer added: %s' % transfer)

        wm = pyinotify.WatchManager()
        mask = pyinotify.IN_CLOSE_WRITE

        handler = EventHandler()
        notifier = pyinotify.ThreadedNotifier(wm, handler)

        try:
            notifier.start()
            wdd = wm.add_watch(settings['torrents'], mask, rec=True)

            while True:
                for x in xrange(int(download_interval) / int(clean_interval) - 1):
                    time.sleep(clean_interval)
                    clean_transfers()

                download_files()
        finally:
            notifier.stop()

    clean_transfers()
    add_torrents()

    time.sleep(clean_interval)
    download_files()
    watch_torrents()
