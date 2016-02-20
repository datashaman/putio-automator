# put.io automator

A suite of commands for managing torrents, transfers and files on put.io.

Configure Sickrage to use a Torrent black hole folder. Configure this application to
monitor that folder and download to the same folder used for post-processing in Sickrage.

To the people who installed the first version, apologies for the change in direction. It's a lot easier to rely on *nix cron to schedule things than to fiddle with threads.

## Setup

Create a virtualenv (recommended, assuming you're using virtualenvwrapper):

    mkvirtualenv putio

Install the package requirements (while being in the virtualenv):

    pip install -r requirements.txt

## Configure

Copy the distributed config file:

    cp config.py.dist config.py

Edit the config in the file. If you do not specify a LOG_FILENAME, the application will log to the console.

To get a put.io token [register your application](https://put.io/v2/oauth2/register) in put.io, and copy the *Oauth token*.

## Run

Run the application (while in virtualenv):

    python manage.py command

Where command is one of the following:

*   **torrents_add**

    Adds existing torrents to put.io.

*   **torrents_watch** [ --add_first=True ]

    Watches torrents folder to add to put.io. By default, adds existing torrents first.

*   **transfers_cancel_seeding**

    Cancels seeding transfers on put.io.

*   **transfers_clean**

    Cleans your transfers list on put.io.

*   **transfers_groom**

    Cancels seeding and then cleans your transfers list on put.io.

*   **files_download** [ --limit n ] [ --chunk_size 256 ]

    Downloads files from put.io (optionally limited, or with chunk size of 256KB).

*   **files_list**

    Shows JSON of the files available for download on put.io.

If the application has encountered a file before, it logs a warning and moves on. Downloads and torrent uploads are recorded in a sqlite3 database: application.db (configurable).

## Operations

The *etc* folder contains a supervisor config file for a watcher and a downloader, as well as a cron file for cron.d with a suggested schedule.

The cron file uses flock so the jobs don't run over eachother if they take a long time (transfer grooming should not take long, though).

I get cheaper bandwidth at an offpeak time, so I schedule my downloads to happen between midnight and 6AM.

The *downloader* program in supervisor does **not** start automatically. At 5 minutes past midnight, cron starts the downloader using *supervisorctl*. Then at 5 minutes to 6AM, it stops it.

If an exception is thrown during the download process, the supervisor program restarts. There is a retry with backoff built into the *downloader*, so you could lose connectivity to
the server for up to 2 minutes and the download will continue.

If the *downloader* program continues to completion, the program stays stopped until the next day.

The chunk size for HTTP traffic is set to *256KB* by default, YMMV. You can change the default in the *files_download* command.
