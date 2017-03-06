"""
Flask commands for managing Put.IO account
"""

import json

from flask_script import Manager
from putio_automator import date_handler
from putio_automator.manage import app

manager = Manager(usage='Manage account')


@manager.command
def info():
    "Show account info"
    print json.dumps(app.client.Account.info(), indent=4, default=date_handler)
