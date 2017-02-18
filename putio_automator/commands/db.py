import sqlite3

from flask_script import Manager
from putio_automator.manage import app


manager = Manager(usage='Manage download database')

@manager.command
def forget(name):
    "Delete records of previous downloads in the database"
    with sqlite3.connect(app.config['DATABASE']) as connection:
        c = connection.cursor()
        c.execute('delete from downloads where name like ?', ('%%%s%%' % name,))
        print 'Affected rows: %s' % c.rowcount
