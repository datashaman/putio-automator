#!/usr/bin/env python
"""
Flask script aka CLI entry module.
"""

import distutils.dir_util
import logging
import os

from flask_script import Manager, prompt
from logging.handlers import RotatingFileHandler
from putio_automator import create_app, APP_NAME, APP_AUTHOR

import appdirs

app = create_app()

manager = Manager(app, usage='Manage torrents and downloads on Put.io')

# This must be here (circular references)
from . import commands

manager.add_command('account', commands.account)
manager.add_command('config', commands.config)
manager.add_command('db', commands.db)
manager.add_command('files', commands.files)
manager.add_command('torrents', commands.torrents)
manager.add_command('transfers', commands.transfers)

def main():
    "Main entry point"
    log_dir = os.getenv('LOG_DIR', appdirs.user_log_dir(APP_NAME, APP_AUTHOR))
    distutils.dir_util.mkpath(log_dir)

    logfile_path = os.path.join(log_dir, 'application.log')

    handler = RotatingFileHandler(logfile_path, maxBytes=10000000, backupCount=5)

    formatter = logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
    handler.setFormatter(formatter)

    handler.setLevel(app.config.get('LOG_LEVEL', logging.WARNING))

    app.logger.addHandler(handler)

    manager.run()

if __name__ == '__main__':
    main()
