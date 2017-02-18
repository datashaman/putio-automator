import subprocess
from flask_script import Manager

manager = Manager(usage='Manage docker instance')


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

