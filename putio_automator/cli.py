#!/usr/bin/env python
"""
CLI entry module.
"""

import click
import importlib.util
import logging
import os
import putiopy

from . import find_config

config_file = find_config()
spec = importlib.util.spec_from_file_location('config', config_file)
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)


@click.group()
@click.option('--token', help='OAuth token')
@click.option('--root', help='ID of folder used as root for commands')
@click.option('--downloads', help='Folder where downloads are stored')
@click.option('--incomplete', help='Folder where incomplete downloads are stored')
@click.option('--torrents', help='Folder where torrents are stored')
@click.option('--log-filename', default='putio.log', help='Filename where log output is written')
@click.option('--log-level', help='Log level used')
@click.pass_context
def cli(ctx, token=None, root=None, downloads=None, incomplete=None, torrents=None, log_filename='putio.log', log_level=None):
    ctx.ensure_object(dict)

    if token is None:
        token = config.PUTIO_TOKEN
    if root is None:
        root = config.PUTIO_ROOT
    if downloads is None:
        downloads = config.DOWNLOADS
    if incomplete is None:
        incomplete = config.INCOMPLETE
    if torrents is None:
        torrents = config.TORRENTS
    if log_level is None:
        log_level = config.LOG_LEVEL

    ctx.obj['CLIENT'] = putiopy.Client(token, use_retry=True)

    ctx.obj['ROOT'] = root
    ctx.obj['DOWNLOADS'] = downloads
    ctx.obj['INCOMPLETE'] = incomplete
    ctx.obj['TORRENTS'] = torrents

    logging.basicConfig(filename=log_filename, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=log_level)

from . import commands

def main():
    cli(auto_envvar_prefix='PUTIO', obj={})
