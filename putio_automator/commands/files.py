"""
Command for managing files on Put.IO.
"""
import click
import json
import os
import shutil
import yaml
 
from putio_automator import date_handler, echo, logger
from putio_automator.cli import cli
from putio_automator.db import with_db


@cli.group()
def files():
    pass

@files.command()
@click.pass_context
@click.option('--parent-id', help='ID of folder to list, defaults to root folder', type=int)
def list(ctx, parent_id=None):
    "List files"
    if parent_id == None:
        parent_id = ctx.obj['ROOT']
    files = ctx.obj['CLIENT'].File.list(parent_id)
    click.echo(yaml.dump([vars(f) for f in files]))

@files.command()
@click.pass_context
@click.option('--limit', help='Limit number of files to be downloaded', type=int)
@click.option('--chunk-size', default=256, help='Chunk size for downloading files in kilobytes')
@click.option('--parent-id', help='ID of folder to download from, defaults to root folder', type=int)
@click.option('--folder', default='', help='Local subfolder to store downloads')
@click.option('--force', help='Force download if it has been seen before, ignores database', is_flag=True)
def download(ctx, limit=None, chunk_size=256, parent_id=None, folder="", force=False):
    "Download files"
    if parent_id == None:
        parent_id = ctx.obj['ROOT']
    files = ctx.obj['CLIENT'].File.list(parent_id)

    logger.info('%s files found' % len(files))

    if len(files):
        def func(connection):
            "Anonymous func"
            if limit is not None:
                downloaded = 0

            conn = connection.cursor()

            for current_file in files:
                conn.execute("select datetime(created_at, 'localtime') from downloads where name = ? and size = ?", (current_file.name, current_file.size))
                row = conn.fetchone()

                if row is None or force:
                    logger.debug('downloading file: %s' % current_file.name)
                    current_file.download(dest=ctx.obj['INCOMPLETE'], delete_after_download=True, chunk_size=int(chunk_size)*1024)
                    logger.info('downloaded file: %s' % current_file.name)

                    src = os.path.join(ctx.obj['INCOMPLETE'], current_file.name)
                    dest = os.path.join(ctx.obj['DOWNLOADS'], folder)
                    shutil.move(src, dest)

                    conn.execute('insert into downloads (id, name, size) values (?, ?, ?)', (current_file.id, current_file.name, current_file.size))
                    connection.commit()

                    if limit is not None:
                        downloaded = downloaded + 1

                        if downloaded > limit:
                            break
                else:
                    logger.warning('file already downloaded at %s : %s' % (row[0], current_file.name))

        with_db(func)
