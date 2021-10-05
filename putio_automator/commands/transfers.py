"""
Flask commands for managing transfers on Put.IO.
"""
import click
import yaml

from putio_automator import date_handler
from putio_automator.cli import cli


@cli.group()
def transfers():
    pass

@transfers.command()
@click.pass_context
def cancel_by_status(ctx, statuses):
    "Cancel transfers by status"

    if isinstance(statuses, str):
        statuses = statuses.split(',')

    transfer_ids = []
    for transfer in ctx.obj['CLIENT'].Transfer.list():
        if transfer.status in statuses:
            transfer_ids.append(transfer.id)

    if len(transfer_ids):
        ctx.obj['CLIENT'].Transfer.cancel_multi(transfer_ids)

@transfers.command()
def cancel_completed():
    "Cancel completed transfers"
    cancel_by_status('COMPLETED')

@transfers.command()
def cancel_seeding():
    "Cancel seeding transfers"
    cancel_by_status('SEEDING')

@transfers.command()
@click.pass_context
def clean(ctx):
    "Clean finished transfers"
    ctx.obj['CLIENT'].Transfer.clean()

@transfers.command()
@click.pass_context
def groom(ctx):
    "Cancel seeding and completed transfers, and clean afterwards"
    ctx.invoke(cancel_by_status, ['SEEDING', 'COMPLETED'])
    ctx.invoke(clean)

@transfers.command()
@click.pass_context
def list(ctx):
    "List transfers"
    transfers = ctx.obj['CLIENT'].Transfer.list()
    click.echo(yaml.dump([vars(t) for t in transfers]))
