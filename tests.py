try:
    import putiopy as putio
except ImportError:
    import putio

import os
import shutil
import tempfile
import unittest

from app import app, init_db
from contextlib import contextmanager
from flask import appcontext_pushed, g, current_app
from manage import torrents_add, init_client
from mock import MagicMock

class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        app.config['TORRENTS'] = tempfile.mkdtemp()
        self.app = app.test_client()
        init_db()
        self.client = init_client(putio.Client('123456'))

    def tearDown(self):
        os.close(self.fd)
        os.unlink(app.config['DATABASE'])

    def test_torrents_add(self):
        self.client.Transfer = MagicMock(return_value='yo')
        shutil.copy(os.path.join('fixtures', 'sample.torrent'), app.config['TORRENTS'])
        torrents_add()

if __name__ == '__main__':
    unittest.main()
