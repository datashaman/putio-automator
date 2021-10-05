"""
Flask commands to manage the download database
"""
import click

from putio_automator import echo, logger
from putio_automator.cli import cli
from putio_automator.db import with_db


@cli.group()
def db():
    pass

@db.command()
@click.argument('name')
def forget(name):
    "Delete records of previous downloads in the database"

    def func(connection):
        "Do the above"
        logger.debug('Delete downloads with name like %s' % name)
        conn = connection.cursor()
        conn.execute('delete from downloads where name like ?', ('%%%s%%' % name,))
        echo('info', 'Deleted %d rows with name like %s' % (conn.rowcount, name))

    with_db(func)
