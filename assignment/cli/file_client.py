import requests
import click
import logging
from .errors import handle_error
import uuid

logger = logging.getLogger(__name__)

def validate_uuid(uuid_str):
    try:
        uuid.UUID(uuid_str)
        return True
    except ValueError:
        return False

def stat_rest(uuid_str, base_url, output="-"):
    try:
        url = f"{base_url.rstrip('/')}/file/{uuid_str}/stat/"
        resp = requests.get(url, timeout=30)
        if resp.status_code == 404:
            handle_error("File not found")
        resp.raise_for_status()
        data = resp.json()
        text = (
            f"Name: {data.get('name','Unknown')}\n"
            f"Size: {data.get('size',0)} bytes\n"
            f"MIME Type: {data.get('mimetype','Unknown')}\n"
            f"Created: {data.get('create_datetime','Unknown')}"
        )
        if output == "-":
            click.echo(text)
        else:
            with open(output, "w") as f:
                f.write(text)
            logger.info(f"Metadata saved to {output}")
    except requests.RequestException as e:
        handle_error(f"REST request failed: {e}")

def read_rest(uuid_str, base_url, output="-"):
    try:
        url = f"{base_url.rstrip('/')}/file/{uuid_str}/read/"
        resp = requests.get(url, timeout=30)
        if resp.status_code == 404:
            handle_error("File not found")
        resp.raise_for_status()
        if output == "-":
            click.echo(resp.text)
        else:
            with open(output, "wb") as f:
                f.write(resp.content)
            logger.info(f"Content saved to {output}")
    except requests.RequestException as e:
        handle_error(f"REST request failed: {e}")

def stat_grpc(*args, **kwargs):
    handle_error("gRPC backend not implemented")

def read_grpc(*args, **kwargs):
    handle_error("gRPC backend not implemented")
