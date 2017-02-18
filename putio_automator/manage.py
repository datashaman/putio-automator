#!/usr/bin/env python

import appdirs
import datetime
import distutils.dir_util
import json
import logging
import os
import pbr
import pbr.packaging
import pyinotify
import shutil
import sqlite3

try:
    import putiopy as putio
except ImportError:
    import putio

from flask import g
from flask_script import Manager, prompt
from json import load
from urllib2 import urlopen
from putio_automator import create_app, APP_NAME, APP_AUTHOR



app = create_app()

manager = Manager(app, usage='Manage torrents and downloads on Put.io')

@manager.command
def init():
    dirs = appdirs.AppDirs(APP_NAME, APP_AUTHOR)

    incomplete = os.path.realpath(prompt('Incomplete directory', 'incomplete'))
    downloads = os.path.realpath(prompt('Downloads directory', 'downloads'))
    torrents = os.path.realpath(prompt('Torrents directory', 'torrents'))

    putio_token = prompt('OAuth Token')

    distutils.dir_util.mkpath(dirs.user_data_dir)

    config_path = os.path.realpath(prompt('Config file to write', os.path.join(dirs.user_data_dir, 'config.py')))

    with open(os.path.join(app.config['BASE_DIR'], 'config.py.dist'), 'r') as source:
        contents = (source.read()
            .replace("os.getenv('PUTIO_TOKEN')", "os.getenv('PUTIO_TOKEN', '" + putio_token + "')")
            .replace("/data/downloads", downloads)
            .replace("/data/incomplete", incomplete)
            .replace("/data/torrents", torrents))

        with open(config_path, 'w') as destination:
            destination.write(contents)

        os.chmod(config_path, 600)

import commands

manager.add_command('db', commands.db)
manager.add_command('docker', commands.docker)
manager.add_command('files', commands.files)
manager.add_command('torrents', commands.torrents)
manager.add_command('transfers', commands.transfers)

def main():
    # format='%(asctime)s | %(levelname)-8s | %(name)-12s | %(message)s')
    manager.run()

if __name__ == '__main__':
    main()
