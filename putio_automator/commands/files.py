import json
import sqlite3

from flask_script import Manager
from putio_automator import date_handler
from putio_automator.db import with_db
from putio_automator.manage import app


manager = Manager(usage='Manage files')

@manager.command
def list(parent_id=0):
    "List files"
    files = app.client.File.list(parent_id)
    print json.dumps([vars(f) for f in files], indent=4, default=date_handler)

@manager.command
def download(limit=None, chunk_size=256, parent_id=0):
    "Download files"
    files = app.client.File.list(parent_id)
    app.logger.info('%s files found' % len(files))

    if len(files):
        def func(connection):
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

        with_db(app, func)
