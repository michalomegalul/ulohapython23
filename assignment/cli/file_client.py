import click
import requests
import sys
from typing import Optional

@click.group()
def file_client():
    """File client for REST/gRPC operations"""
    pass

@file_client.command()
@click.argument('uuid')
@click.option('--backend', type=click.Choice(['rest', 'grpc']), default='grpc', 
              help='Backend to use (default: grpc)')
@click.option('--grpc-server', default='localhost:50051', 
              help='gRPC server address (default: localhost:50051)')
@click.option('--base-url', default='http://localhost/', 
              help='REST API base URL (default: http://localhost/)')
@click.option('--output', default='-', 
              help='Output file (default: stdout)')
def stat(uuid: str, backend: str, grpc_server: str, base_url: str, output: str):
    """Prints the file metadata in a human-readable manner."""
    
    if backend == 'rest':
        _stat_rest(uuid, base_url, output)
    else:
        _stat_grpc(uuid, grpc_server, output)

@file_client.command()
@click.argument('uuid')
@click.option('--backend', type=click.Choice(['rest', 'grpc']), default='grpc',
              help='Backend to use (default: grpc)')
@click.option('--grpc-server', default='localhost:50051',
              help='gRPC server address (default: localhost:50051)')
@click.option('--base-url', default='http://localhost/',
              help='REST API base URL (default: http://localhost/)')
@click.option('--output', default='-',
              help='Output file (default: stdout)')
def read(uuid: str, backend: str, grpc_server: str, base_url: str, output: str):
    """Outputs the file content."""
    
    if backend == 'rest':
        _read_rest(uuid, base_url, output)
    else:
        _read_grpc(uuid, grpc_server, output)

def _stat_rest(uuid: str, base_url: str, output: str):
    """Get file stats via REST API"""
    try:
        url = f"{base_url.rstrip('/')}/file/{uuid}/stat/"
        response = requests.get(url)
        
        if response.status_code == 404:
            click.echo("File not found", err=True)
            sys.exit(1)
        
        response.raise_for_status()
        data = response.json()
        
        output_text = f"""File Metadata:
  Name: {data.get('name', 'Unknown')}
  Size: {data.get('size', 0)} bytes
  MIME Type: {data.get('mimetype', 'Unknown')}
  Created: {data.get('create_datetime', 'Unknown')}
"""
        
        if output == '-':
            click.echo(output_text)
        else:
            with open(output, 'w') as f:
                f.write(output_text)
                
    except requests.RequestException as e:
        click.echo(f"Error connecting to REST API: {e}", err=True)
        sys.exit(1)

def _read_rest(uuid: str, base_url: str, output: str):
    """Read file content via REST API"""
    try:
        url = f"{base_url.rstrip('/')}/file/{uuid}/read/"
        response = requests.get(url)
        
        if response.status_code == 404:
            click.echo("File not found", err=True)
            sys.exit(1)
            
        response.raise_for_status()
        
        if output == '-':
            click.echo(response.text)
        else:
            with open(output, 'wb') as f:
                f.write(response.content)
                
    except requests.RequestException as e:
        click.echo(f"Error connecting to REST API: {e}", err=True)
        sys.exit(1)

def _stat_grpc(uuid: str, grpc_server: str, output: str):
    """Get file stats via gRPC (placeholder)"""
    click.echo("gRPC support coming soon!", err=True)
    sys.exit(1)

def _read_grpc(uuid: str, grpc_server: str, output: str):
    """Read file content via gRPC (placeholder)"""
    click.echo("gRPC support coming soon!", err=True)
    sys.exit(1)

if __name__ == '__main__':
    file_client()