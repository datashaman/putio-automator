# put.io automater #

This small python application monitors a folder for torrent files. When one is saved there,
it uploads the torrent file to put.io, which starts a transfer. Every minute or so, it
checks your put.io files collection for new files and downloads one to a downloads folder.

# Setup #

Create a virtualenv (recommended):

    mkvirtualenv putio

Install the package requirements (while being in the virtualenv):

    pip install -r requirements.txt

# Configure #

Copy the distributed .ini file:

    cp application.ini.dist application.ini

Edit the config settings in the file. If you do not specify a log_filename, the application will log to the console.

To get a put.io token [register your application](https://put.io/v2/oauth2/register) in put.io, and copy the *Oauth token*.
