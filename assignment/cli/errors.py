import click
import logging
import sys

logger = logging.getLogger(__name__)

def handle_error(message: str, exit_code: int = 1):
    """Log error and exit"""
    logger.error(message)
    click.echo(f"Error: {message}", err=True)
    sys.exit(exit_code)
