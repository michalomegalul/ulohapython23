import click
import requests
import sys
import json
from typing import Optional

@click.group()
@click.option('--backend', type=click.Choice(['rest', 'grpc']), default='grpc',
              help='Set a backend to be used, choices are grpc and rest. Default is grpc.')
@click.option('--grpc-server', default='localhost:50051',
              help='Set a host and port of the gRPC server. Default is localhost:50051.')
@click.option('--base-url', default='http://localhost/',
              help='Set a base URL for a REST server. Default is http://localhost/.')
@click.option('--output', default='-',
              help='Set the file where to store the output. Default is -, i.e. the stdout.')
@click.pass_context
def file_client(ctx, backend, grpc_server, base_url, output):
    """File client for REST/gRPC operations"""
    # Store options in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj['backend'] = backend
    ctx.obj['grpc_server'] = grpc_server
    ctx.obj['base_url'] = base_url
    ctx.obj['output'] = output

@file_client.command()
@click.argument('uuid')
@click.pass_context
def stat(ctx, uuid):
    """Prints the file metadata in a human-readable manner."""
    backend = ctx.obj['backend']
    
    if backend == 'rest':
        _stat_rest(uuid, ctx.obj['base_url'], ctx.obj['output'])
    else:
        _stat_grpc(uuid, ctx.obj['grpc_server'], ctx.obj['output'])

@file_client.command()
@click.argument('uuid')
@click.pass_context
def read(ctx, uuid):
    """Outputs the file content."""
    backend = ctx.obj['backend']
    
    if backend == 'rest':
        _read_rest(uuid, ctx.obj['base_url'], ctx.obj['output'])
    else:
        _read_grpc(uuid, ctx.obj['grpc_server'], ctx.obj['output'])

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
        
        # Format metadata in human-readable way
        output_text = f"""File Metadata:
  Name: {data.get('name', 'Unknown')}
  Size: {data.get('size', 0)} bytes
  MIME Type: {data.get('mimetype', 'Unknown')}
  Created: {data.get('create_datetime', 'Unknown')}
"""
        
        if output == '-':
            click.echo(output_text.rstrip())
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
            # Output to stdout
            click.echo(response.text.rstrip())
        else:
            # Save to file
            with open(output, 'wb') as f:
                f.write(response.content)
                
    except requests.RequestException as e:
        click.echo(f"Error connecting to REST API: {e}", err=True)
        sys.exit(1)

def _stat_grpc(uuid: str, grpc_server: str, output: str):
    """Get file stats via gRPC (not implemented)"""
    click.echo("gRPC backend not implemented yet", err=True)
    sys.exit(1)

def _read_grpc(uuid: str, grpc_server: str, output: str):
    """Read file content via gRPC (not implemented)"""
    click.echo("gRPC backend not implemented yet", err=True)
    sys.exit(1)

if __name__ == '__main__':
    file_client()