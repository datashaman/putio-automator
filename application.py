import ConfigParser
import logging
import os
import putio
import pyinotify

config = ConfigParser.ConfigParser()
config.read('application.ini')

settings = dict(config.items('settings'))

logging.basicConfig(filename=settings.get('log_filename', None), level=logging.INFO)

client = putio.Client(settings['putio_token'])

def download_file(notifier):
    files = client.File.list()

    # Download and delete just one at a time
    if len(files):
        file = files[0]
        logging.debug('downloading file: %s' % file)
        file.download(dest=settings['downloads'], delete_after_download=True)
        logging.info('downloaded file: %s' % file)

class EventHandler(pyinotify.ProcessEvent):
    def process_IN_CLOSE_WRITE(self, event):
        logging.debug('received event: %s' % event)
        transfer = client.Transfer.add_torrent(event.pathname)
        logging.info('transfer added: %s' % transfer)

wm = pyinotify.WatchManager()
mask = pyinotify.IN_CLOSE_WRITE

handler = EventHandler()
notifier = pyinotify.Notifier(wm, handler)

wdd = wm.add_watch(settings['torrents'], mask, rec=True)

notifier.loop(download_file)
