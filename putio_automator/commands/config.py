"""
Flask commands for managing config of the application
"""

import appdirs
import click
import json
import os
import stat

from putio_automator import APP_NAME, APP_AUTHOR, date_handler, echo, find_config, logger
from putio_automator.cli import cli


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

@cli.group()
def config():
    pass

@config.command()
def init(site=False):
    "Prompt the user for config"

    if site:
        base_dir = appdirs.site_data_dir(APP_NAME, APP_AUTHOR)
    else:
        base_dir = appdirs.user_data_dir(APP_NAME, APP_AUTHOR)

    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    config_path = os.path.join(base_dir, 'config.py')

    incomplete = os.path.realpath(click.prompt('Incomplete directory', 'incomplete'))
    downloads = os.path.realpath(click.prompt('Downloads directory', 'downloads'))
    torrents = os.path.realpath(click.prompt('Torrents directory', 'torrents'))

    putio_token = click.prompt('OAuth Token')

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

    echo('info', 'Config written to %s' % config_path)

@config.command()
def show():
    "Show config filename and current config"
    config_file = find_config(verbose=True)

    if config_file:
        echo('info', 'Found config file at %s' % config_file)
    else:
        echo('error', 'Config file not found')

    # logger.info('Current config:\n%s' % json.dumps(app.config, indent=4, default=date_handler))
