import appdirs
import os
import stat

from flask_script import Manager, prompt
from putio_automator import APP_NAME, APP_AUTHOR
from putio_automator.manage import app

manager = Manager(usage='Manage configuration')


@manager.command
def init():
    user_data_dir = appdirs.user_data_dir(APP_NAME, APP_AUTHOR)

    incomplete = os.path.realpath(prompt('Incomplete directory', 'incomplete'))
    downloads = os.path.realpath(prompt('Downloads directory', 'downloads'))
    torrents = os.path.realpath(prompt('Torrents directory', 'torrents'))

    putio_token = prompt('OAuth Token')

    config_path = os.path.realpath(prompt('Config file to write', os.path.join(user_data_dir, 'config.py')))

    root = os.getenv('VIRTUAL_ENV')

    if root is None:
        root = '/'

    with open(os.path.join(root, 'etc', 'putio-automator', 'config.py.dist'), 'r') as source:
        contents = (source.read()
            .replace("os.getenv('PUTIO_TOKEN')", "os.getenv('PUTIO_TOKEN', '" + putio_token + "')")
            .replace("/files/downloads", downloads)
            .replace("/files/incomplete", incomplete)
            .replace("/files/torrents", torrents))

        with open(config_path, 'w') as destination:
            destination.write(contents)

        os.chmod(config_path, stat.S_IRUSR | stat.S_IWUSR)
