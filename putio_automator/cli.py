#!/usr/bin/env python
"""
Flask script aka CLI entry module.
"""

import click
import logging
import os
import putiopy

from dotenv import load_dotenv

dotenv_path = os.path.join(os.getcwd(), '.env')
if os.path.isfile(dotenv_path):
    load_dotenv(dotenv_path)

@click.group()
@click.option('--token')
@click.option('--root')
@click.option('--downloads')
@click.option('--incomplete')
@click.option('--torrents')
@click.pass_context
def cli(ctx, token=None, root=0, downloads='downloads', incomplete='incomplete', torrents='torrents', log_filename='putio.log', log_level='WARNING'):
    ctx.ensure_object(dict)
    ctx.obj['CLIENT'] = putiopy.Client(token, use_retry=True)
    ctx.obj['ROOT'] = root
    ctx.obj['DOWNLOADS'] = downloads
    ctx.obj['INCOMPLETE'] = incomplete
    ctx.obj['TORRENTS'] = torrents

    logging.basicConfig(filename=log_filename, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=log_level)

from . import commands

def main():
    cli(auto_envvar_prefix='PUTIO', obj={})
