"""
Flask commands for managing config of the application
"""

import json
import os
import stat

from flask_script import Manager, prompt
from putio_automator import APP_NAME, APP_AUTHOR, date_handler, find_config
from putio_automator.manage import app

import appdirs


manager = Manager(usage='Manage configuration')

def find_config_dist():
    "Search for the config.py.dist file"
    search_paths = [
        os.path.join(os.getcwd(), 'etc', 'config.py.dist'),
        os.path.join(os.getenv('HOME'), '.local', 'share', APP_NAME, 'config.py.dist'),
        os.path.join('/etc', APP_NAME, 'config.py.dist'),
    ]

    config = None

    for search_path in search_paths:
        if os.path.exists(search_path) and not os.path.isdir(search_path):
            config = search_path
            break

    return config

@manager.command
def init(site=False):
    "Prompt the user for config"

    if site:
        base_dir = appdirs.site_data_dir(APP_NAME, APP_AUTHOR)
    else:
        base_dir = appdirs.user_data_dir(APP_NAME, APP_AUTHOR)

    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    config_path = os.path.join(base_dir, 'config.py')

    incomplete = os.path.realpath(prompt('Incomplete directory', 'incomplete'))
    downloads = os.path.realpath(prompt('Downloads directory', 'downloads'))
    torrents = os.path.realpath(prompt('Torrents directory', 'torrents'))

    putio_token = prompt('OAuth Token')

    config_dist = find_config_dist()
    with open(config_dist, 'r') as source:
        contents = (source.read()
                    .replace("os.getenv('PUTIO_TOKEN')",
                             "os.getenv('PUTIO_TOKEN', '" + putio_token + "')")
                    .replace("/files/downloads", downloads)
                    .replace("/files/incomplete", incomplete)
                    .replace("/files/torrents", torrents))

        with open(config_path, 'w') as destination:
            destination.write(contents)

        os.chmod(config_path, stat.S_IRUSR | stat.S_IWUSR)

        print '\nConfig written to %s' % config_path


@manager.command
def show():
    "Show config filename and current config"
    config_file = find_config(verbose=True)
    print 'Config filename: %s' % config_file
    print 'Current config:\n%s' % json.dumps(app.config, indent=4, default=date_handler)
