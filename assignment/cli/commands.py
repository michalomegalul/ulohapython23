import click
import os
from datetime import datetime
from .database import DatabaseManager
from .file_client import file_client

@click.group()
@click.version_option(version='1.0.0')
def cli():
    """Domain Management CLI Tool by michalomegalul"""
    pass

@cli.command()
def status():
    """Check database connection and show statistics"""
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    click.echo(f"[{timestamp} UTC] Checking system status...")
    
    # Show app info
    click.echo("Author: michalomegalul")
    click.echo("Version: 1.0.0")
    
    try:
        db = DatabaseManager()
        stats = db.get_system_stats()

        click.echo(click.style("Database connection successful", fg='green'))
        click.echo(f"  Total domains: {stats['total_domains']}")
        click.echo(f"  Active domains: {stats['active_domains']}")
        click.echo(f"  Total flags: {stats['total_flags']}")
        click.echo(f"  Active flags: {stats['active_flags']}")
    except Exception as e:
        click.echo(click.style(f"Database connection failed: {e}", fg='red'))

@cli.command()
def query_active_domains():
    """Query currently registered domains without active EXPIRED flag"""
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    click.echo(f"[{timestamp} UTC] Querying active domains...")
    
    try:
        db = DatabaseManager()
        domains = db.get_active_domains()
        
        if domains:
            click.echo(f"\nFound {len(domains)} active domains:")
            for domain in domains:
                click.echo(f"  • {domain['fqdn']}")
        else:
            click.echo("No active domains found.")
    except Exception as e:
        click.echo(click.style(f"Database error: {e}", fg='red'))

@cli.command()
def query_flagged_domains():
    """Query domains that have had both EXPIRED and OUTZONE flags"""
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    click.echo(f"[{timestamp} UTC] Querying flagged domains...")
    
    try:
        db = DatabaseManager()
        domains = db.get_flagged_domains()
        
        if domains:
            click.echo(f"\nFound {len(domains)} domains with both flags:")
            for domain in domains:
                click.echo(f"  • {domain['fqdn']}")
        else:
            click.echo("No domains found with both flags.")
    except Exception as e:
        click.echo(click.style(f"Database error: {e}", fg='red'))

# Add the file-client as a subcommand
cli.add_command(file_client, name='file-client')

if __name__ == '__main__':
    cli()