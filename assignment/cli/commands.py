import click
from datetime import datetime
from .database import DatabaseManager
from .rest_client import RestAPIClient
#from .grpc_client import GrpcAPIClient
from .file_client import file_client

@click.group()
@click.version_option(version='1.0.0')
def cli():
    """Domain Management CLI Tool"""
    pass

@cli.command()
@click.option('--uuid', required=True, help='UUID to fetch domains data')
@click.option('--api-type', type=click.Choice(['rest', 'grpc']), default='rest', 
              help='API type to use (default: rest)')
def fetch_domains(uuid, api_type):
    """Fetch domains from API and store in database"""
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    click.echo(f"[{timestamp} UTC] Fetching domains for UUID: {uuid} using {api_type.upper()} API")
    
    # Choose API client
    if api_type == 'rest':
        api_client = RestAPIClient()
    else:
        #api_client = GrpcAPIClient()
        click.echo(click.style("gRPC client not implemented yet", err=True, fg='red'))
        api_client = RestAPIClient()
    # Fetch data from API
    data = api_client.fetch_domains(uuid)
    
    if not data:
        click.echo(click.style("No data received from API", fg='red'))
        return

    click.echo(click.style(f" Data received from {data['source']}", fg='green'))

    # Store in database
    db = DatabaseManager()
    stored_count = db.store_domains(data)

    click.echo(click.style(f" Fetch completed - stored {stored_count} new domains", fg='green'))


@cli.command()
def query_active_domains():
    """Query currently registered domains without active EXPIRED flag"""
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    click.echo(f"[{timestamp} UTC] Querying active domains...")
    
    db = DatabaseManager()
    domains = db.get_active_domains()
    
    if domains:
        click.echo(f"\nFound {len(domains)} active domains:")
        for domain in domains:
            click.echo(f"  • {domain['fqdn']}")
    else:
        click.echo("No active domains found.")


@cli.command()
def query_flagged_domains():
    """Query domains that have had both EXPIRED and OUTZONE flags"""
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    click.echo(f"[{timestamp} UTC] Querying flagged domains...")
    
    db = DatabaseManager()
    domains = db.get_flagged_domains()
    
    if domains:
        click.echo(f"\nFound {len(domains)} domains with both flags:")
        for domain in domains:
            click.echo(f"  • {domain['fqdn']}")
    else:
        click.echo("No domains found with both flags.")


@cli.command()
def status():
    """Check database connection and show statistics"""
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    click.echo(f"[{timestamp} UTC] Checking system status...")
    
    db = DatabaseManager()
    stats = db.get_system_stats()

    click.echo(click.style("Database connection successful", fg='green'))
    click.echo(f"  Total domains: {stats['total_domains']}")
    click.echo(f"  Active domains: {stats['active_domains']}")
    click.echo(f"  Total flags: {stats['total_flags']}")
    click.echo(f"  Active flags: {stats['active_flags']}")

# Add file-client as a subcommand
cli.add_command(file_client, name='file-client')

if __name__ == '__main__':
    cli()