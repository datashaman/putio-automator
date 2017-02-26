import os
import subprocess

from flask_script import Manager
from putio_automator import APP_TAG
from putio_automator.manage import app

manager = Manager(usage='Manage docker instance')


@manager.command
def pull(tag=APP_TAG):
    "Pull latest application image"
    subprocess.call([
        'docker',
        'pull',
        tag
    ])

@manager.command
def build(tag=APP_TAG):
    "Build an application image"
    subprocess.call([
        'docker',
        'build',
        '-t',
        tag,
        '.'
    ])

@manager.command
@manager.option('-d', '--log-dir', dest='log_dir')
def run(start_hour=0, end_hour=24, check_downloads_every=15, tag=APP_TAG, dir=None, level=None):
    if level is None:
        level = app.config['LOG_LEVEL']

    "Run an application container"
    subprocess.call([
	    'docker',
	    'run',
	    '--rm',
	    '-i',
	    '-e',
	    'START_HOUR=%s' % start_hour,
	    '-e',
	    'END_HOUR=%s' % end_hour,
	    '-e',
	    'CHECK_DOWNLOADS_EVERY=%s' % check_downloads_every,
	    '-e',
	    'LOG_DIR=%s' % dir,
	    '-e',
	    'LOG_LEVEL=%s' % level,
	    '-e',
	    'PUTIO_TOKEN=%s' % app.config['PUTIO_TOKEN'],
	    '-p',
        '9001:9001',
        '-v',
        '%s:/files/incomplete' % app.config['INCOMPLETE'],
        '-v',
        '%s:/files/downloads' % app.config['DOWNLOADS'],
        '-v',
        '%s:/files/torrents' % app.config['TORRENTS'],
        tag
    ])

@manager.command
def bootstrap(start_hour=None, end_hour=None, check_downloads_every=None):
    if start_hour is None:
        start_hour = os.getenv('START_HOUR', 0)

    if end_hour is None:
        end_hour = os.getenv('END_HOUR', 0)

    if check_downloads_every is None:
        check_downloads_every = os.getenv('CHECK_DOWNLOADS_EVERY', 15)

    "Create schedule and start supervisor"
    subprocess.call([
        'cog.py',
        '-r',
        '-D',
        'START_HOUR=%s' % start_hour,
        '-D',
        'END_HOUR=%s' % end_hour,
        '-D',
        'CHECK_DOWNLOADS_EVERY=%s' % check_downloads_every,
        '/etc/cron.d/putio-automator'
    ])

    subprocess.call([
        'supervisord',
        '-n',
        '-c',
        '/etc/supervisor/supervisord.conf',
        '--logfile',
        '/dev/stdout',
        '--logfile_maxbytes',
        '0'
    ])
