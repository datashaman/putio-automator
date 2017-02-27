"""
Flask commands to manage the download database
"""
from flask_script import Manager
from putio_automator.db import with_db
from putio_automator.manage import app


manager = Manager(usage='Manage download database')

@manager.command
def forget(name):
    "Delete records of previous downloads in the database"

    def func(connection):
        "Do the above"
        conn = connection.cursor()
        conn.execute('delete from downloads where name like ?', ('%%%s%%' % name,))
        print 'Affected rows: %s' % conn.rowcount

    with_db(app, func)
