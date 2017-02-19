import subprocess
from flask_script import Manager
from putio_automator import APP_TAG
from putio_automator.manage import app

manager = Manager(usage='Manage docker instance')


@manager.command
def build(tag=APP_TAG):
    subprocess.call([
        'docker',
        'build',
        '-t',
        tag,
        '.'
    ])

@manager.command
def run(start=0, end=23, check_frequency=15, tag=APP_TAG):
	subprocess.call([
	    'docker',
	    'run',
	    '--rm',
	    '-i',
	    '-e',
	    'START_HOUR=%s' % start,
	    '-e',
	    'END_HOUR=%s' % end,
	    '-e',
	    'CHECK_DOWNLOADS_EVERY=%s' % check_frequency,
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
def supervisord():
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

