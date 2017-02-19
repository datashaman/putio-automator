#!/usr/bin/env python

import appdirs
import distutils.dir_util
import os

from flask_script import Manager, prompt
from putio_automator import create_app, APP_NAME, APP_AUTHOR

app = create_app()

manager = Manager(app, usage='Manage torrents and downloads on Put.io')

import commands

manager.add_command('config', commands.config)
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
