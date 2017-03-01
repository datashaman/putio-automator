# put.io automator

A suite of commands for managing torrents, transfers and files on **Put.IO**

Configure Sickrage to use a Torrent black hole folder. Configure this application to
monitor that folder and download to the same folder used for post-processing in Sickrage.

## Table of Contents

<!-- toc -->

* [Installation](#installation)
* [Configuration](#configuration)
* [Regular usage](#regular-usage)
  * [Torrents](#torrents)
  * [Files](#files)
  * [Transfers](#transfers)
  * [Database](#database)
* [Advanced Usage](#advanced-usage)
  * [Docker](#docker)

<!-- toc stop -->

## Installation

Install the putio-automator package locally for your user (recommended):

    pip install --user putio-automator

This will install a new command-line utility `putio` in `$HOME/.local/bin`. Ensure it's on your path:

    echo 'PATH=$HOME/.local/bin:$PATH' >> .profile # or .bashrc or .zshrc, ymmv

Or for all users on your machine (not recommended):

    sudo -H pip install putio-automator

This will install a new command-line utility `putio` in `/usr/local/bin` or similar. It should be on your path already.

## Configuration

Initialize the application with a basic configuration:

    putio config init

This will interactively prompt you with some questions about where files should be stored, and your **Put.IO** `OAuth Token`.

To get an `OAuth Token` register your application on **Put.IO**, and copy the `OAuth Token` (found under the key icon).

**NB** The directories entered must have world-write permissions (until I figure out how to do permissions cleanly).

Check that the connection is working:

    putio account info

You should see a JSON packet with information about your account. If not, check your `OAuth Token` is correct.

To help you debug config issues, show the current config:

    putio config show

## Regular usage

### Torrents

Watch configured directory for torrents and add to **Put.IO**:

    putio torrents watch [-a] [-p PARENT_ID]

* -a, --add_existing
  Add existing torrents first.
* -p PARENT_ID, --parent_id PARENT_ID
  Parent folder to add files to.

Add existing torrents to **Put.IO**:

    putio torrents add [-p PARENT_ID]

* -p PARENT_ID, --parent_id PARENT_ID
  Parent folder to add files to.

### Files

List files on **Put.IO**:

    putio files list [-p PARENT_ID]

* -p PARENT_ID, --parent_id PARENT_ID
  Parent folder to list files from.

Download files from **Put.IO** to configured downloads directory:

    putio files download [-l LIMIT] [-c CHUNK_SIZE] [-p PARENT_ID]

* -l LIMIT, --limit LIMIT
  Maximum number of files to download in one go.
* -c CHUNK_SIZE, --chunk_size CHUNK_SIZE
  Defaults to 256kb.
* -p PARENT_ID, --parent_id PARENT_ID
  Parent folder to download files from.

### Transfers

List transfers on **Put.IO**:

    putio transfers list

Cancel by status:

    putio transfers cancel_by_status statuses

* statuses
  Comma-delimited list of statuses.

Cancel completed transfers:

    putio transfers cancel_completed

Cancel seeding transfers:

    putio transfers cancel_seeding

Clean finished transfers:

    putio transfers clean

Groom transfers (cancels seeding and completed transfers, and cleans afterwards):

    putio transfers groom

### Database

The application records downloads in a SQLite database, so you don't inadvertently download the same file over and over when there's an error. This command clears the database record of a specific substring so you can download it again:

    putio db forget name

* name
  A substring found in the filename.

## Advanced Usage

### Docker

To pull the latest docker image:

    putio docker pull

To run an application container that manages downloads for you on an optional schedule:

    putio docker run [-s START_HOUR] [-e END_HOUR] [-c CHECK_DOWNLOADS_EVERY] [-t TAG]

* -s START_HOUR, --start_hour START_HOUR
  The hour to start downloads. Defaults to 0.
* -e END_HOUR, --end_hour END_HOUR
  The hour to end downloads. Defaults to 24 (same as 0).
* -c CHECK_DOWNLOADS_EVERY, --check_downloads_every CHECK_DOWNLOADS_EVERY.
  Defaults to 15 (minutes).
* -t TAG, --tag TAG
  Defaults to datashaman/putio-automator.

The docker container will use your configured directories to watch for torrents and download files. You can view the supervisor console at [http://localhost:9001](http://localhost:9001).

