"""
Flask commands for managing Put.IO account
"""

import click
import yaml
import putiopy
import sys

from putio_automator import date_handler, echo, logger
from putio_automator.cli import cli


@cli.group()
def account():
    pass

@account.command()
@click.pass_context
def info(ctx):
    "Show account info"
    try:
        response = ctx.obj['CLIENT'].Account.info()
    except putiopy.ClientError as exc:
        echo('error', exc.message)
        ctx.exit(1)

    if response['status'] == 'OK':
        echo('info', yaml.dump(response['info']))
    else:
        echo('error', yaml.dump(response))
        ctx.exit(1)
