"""
Flask command for managing files on Put.IO.
"""
import json
import os
import shutil
 
from flask_script import Command, Manager
from putio_automator import date_handler
from putio_automator.db import with_db
from putio_automator.manage import app


manager = Manager(usage='Manage files')

class List(Command):
    "List files: Create a Flask command manually - clashes with list"
    def run(self, parent_id=0):
        "Run the command"
        files = app.client.File.list(parent_id)
        print json.dumps([vars(f) for f in files], indent=4, default=date_handler)

manager.add_command('list', List())

@manager.command
def download(limit=None, chunk_size=256, parent_id=0, folder=""):
    "Download files"
    files = app.client.File.list(parent_id)
    app.logger.info('%s files found' % len(files))

    if len(files):
        def func(connection):
            "Anonymous func"
            if limit is not None:
                downloaded = 0

            conn = connection.cursor()

            for current_file in files:
                conn.execute("select datetime(created_at, 'localtime') from downloads where name = ? and size = ?", (current_file.name, current_file.size))
                row = conn.fetchone()

                if row is None:
                    app.logger.debug('downloading file: %s' % current_file)
                    current_file.download(dest=app.config['INCOMPLETE'], delete_after_download=True, chunk_size=int(chunk_size)*1024)
                    app.logger.info('downloaded file: %s' % current_file)

                    src = os.path.join(app.config['INCOMPLETE'], current_file.name)
                    dest = os.path.join(app.config['DOWNLOADS'], folder)
                    shutil.move(src, dest)

                    conn.execute('insert into downloads (id, name, size) values (?, ?, ?)', (current_file.id, current_file.name, current_file.size))
                    connection.commit()

                    if limit is not None:
                        downloaded = downloaded + 1

                        if downloaded > limit:
                            break
                else:
                    app.logger.warning('file already downloaded at %s : %s' % (row[0], current_file))

        with_db(app, func)
