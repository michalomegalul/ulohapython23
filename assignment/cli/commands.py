import click
from datetime import datetime
from .db import DatabaseManager
from .file_client import stat_rest, read_rest, stat_grpc, read_grpc, validate_uuid
from .errors import handle_error
import logging

logger = logging.getLogger(__name__)

@click.group()
@click.version_option(version="1.0.0")
@click.option("--verbose", "-v", is_flag=True)
def cli(verbose):
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Logging enabled")

@cli.command()
def status():
    click.echo(f"[{datetime.utcnow()} UTC] Database Status")
    db = DatabaseManager()
    stats = db.get_stats()
    click.echo(f"Domains: {stats['total_domains']} total, {stats['active_domains']} active")
    click.echo(f"Flags: {stats['total_flags']} total")

@cli.command()
def active_domains():
    db = DatabaseManager()
    domains = db.get_active_domains()
    if domains:
        click.echo(f"Active domains ({len(domains)}):")
        for d in domains:
            click.echo(f"  {d}")
    else:
        click.echo("No active domains found")

@cli.command()
def flagged_domains():
    db = DatabaseManager()
    domains = db.get_flagged_domains()
    if domains:
        click.echo(f"Flagged domains ({len(domains)}):")
        for d in domains:
            click.echo(f"  {d}")
    else:
        click.echo("No flagged domains found")

@cli.command()
@click.option("--backend", default="grpc", help="Choose backend: rest or grpc")
@click.option("--grpc-server", default="localhost:50051")
@click.option("--base-url", default="http://localhost/")
@click.option("--output", default="-")
@click.argument("command", type=click.Choice(["stat","read"]))
@click.argument("uuid")
def file_client(backend, grpc_server, base_url, output, command, uuid):
    if not validate_uuid(uuid):
        handle_error("Invalid UUID format")
    if backend == "rest":
        if command == "stat":
            stat_rest(uuid, base_url, output)
        else:
            read_rest(uuid, base_url, output)
    elif backend == "grpc":
        if command == "stat":
            stat_grpc(uuid, grpc_server, output)
        else:
            read_grpc(uuid, grpc_server, output)
    else:
        handle_error(f"Unknown backend '{backend}'")
