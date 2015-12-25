# put.io automator #

A suite of commands for managing torrents, transfers and files on put.io.

The *etc* folder contains a supervisor config file for the watcher, and a cron file for cron.d with a suggested schedule. The cron file uses flock so the jobs don't run over eachother if they take a long time.

Configure Sickrage to use a Torrent black hole folder. Configure this application to
monitor that folder and download to the same folder used for post-processing in Sickrage.

To the people who installed the first version, apologies for the change in direction. It's a lot easier to rely on *nix cron to schedule things than to fiddle with threads.

# Setup #

Create a virtualenv (recommended, assuming you're using virtualenvwrapper):

    mkvirtualenv putio

Install the package requirements (while being in the virtualenv):

    pip install -r requirements.txt

# Configure #

Copy the distributed config file:

    cp config.py.dist config.py

Edit the config in the file. If you do not specify a LOG_FILENAME, the application will log to the console.

To get a put.io token [register your application](https://put.io/v2/oauth2/register) in put.io, and copy the *Oauth token*.

## Run ##

Run the application (while in virtualenv):

    python manage.py command

Where command is one of the following:

*   torrents_add

    Adds existing torrents to put.io.

*   torrents_watch [ --add_first=True ]

    Watches torrents folder to add to put.io. By default, adds existing torrents first.

*   transfers_cancel_seeding

    Cancels seeding transfers on put.io.

*   transfers_clean

    Cleans your transfers list on put.io.

*   transfers_groom

    Cancels seeding and then cleans your transfers list on put.io.

*   files_download [ --limit n ]

    Downloads files from put.io (optionally limited).

If the application has encountered a file before, it logs a warning and moves on. Downloads and torrent uploads are recorded in a sqlite3 database: application.db (configurable).
