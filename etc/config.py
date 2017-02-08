import logging
import os

DATABASE = '/app/run/app.db'
LOG_FILENAME = None
LOG_LEVEL = os.getenv('LOG_LEVEL')

PUTIO_TOKEN = os.getenv('PUTIO_TOKEN')

DOWNLOADS = '/files/downloads'
INCOMPLETE = '/files/incomplete'
TORRENTS = '/files/torrents'

UPNP_PORT = 42000
