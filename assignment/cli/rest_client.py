"""REST API client for File Management"""

import os
import requests
import uuid as uuid_lib
import click
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class RestAPIClient:
    """REST API client for fetching file data"""
    
    def __init__(self):
        # Use environment variable for API base URL
        self.base_url = os.getenv('API_BASE_URL')
        
        if not self.base_url:
            click.echo("Error: API_BASE_URL environment variable not set", err=True, fg='red')
            click.echo("Please check your .env file", err=True, fg='red')

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": f"DomainCLI/{os.getenv('APP_VERSION', '1.0.0')} ({os.getenv('APP_AUTHOR', 'unknown')})",
            "Accept": "application/json"
        })
    
    def validate_uuid(self, uuid_str: str) -> bool:
        """Validate UUID format"""
        try:
            uuid_lib.UUID(uuid_str)
            return True
        except ValueError:
            return False
    
    def fetch_domains(self, uuid_str: str) -> Optional[Dict[str, Any]]:
        """Fetch and process file for domain data"""
        if not self.validate_uuid(uuid_str):
            raise click.BadParameter(f"Invalid UUID format: {uuid_str}")

        # Get metadata
        metadata = self.get_file_metadata(uuid_str)
        if not metadata:
            return None
        
        # Get content
        content = self.download_file_content(uuid_str)
        if not content:
            return None
        
        # Parse and return
        return self._parse_file_content(content, metadata, uuid_str)
    
    def get_file_metadata(self, uuid_str: str) -> Optional[Dict[str, Any]]:
        """Get file metadata from REST API"""
        url = f"{self.base_url}/file/{uuid_str}/stat/"
        
        try:
            click.echo(f"  Getting file metadata from: {url}")
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 404:
                click.echo(f"  File not found for UUID: {uuid_str}")
                return None
            
            response.raise_for_status()
            metadata = response.json()
            
            click.echo(f"    File found: {metadata.get('name', 'Unknown')}", fg='green')
            click.echo(f"    Size: {metadata.get('size', 0)} bytes")
            click.echo(f"    MIME: {metadata.get('mimetype', 'Unknown')}")
            click.echo(f"    Created: {metadata.get('create_datetime', 'Unknown')}")
            
            return metadata
            
        except requests.RequestException as e:
            click.echo(f"  REST API request failed: {e}", err=True, fg='red')
            return None
    
    def download_file_content(self, uuid_str: str) -> Optional[str]:
        """Download file content from REST API"""
        url = f"{self.base_url}/file/{uuid_str}/read/"
        
        try:
            click.echo(f"  Downloading file content from: {url}")
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 404:
                click.echo(f"  File not found for UUID: {uuid_str}")
                return None
            
            response.raise_for_status()
            
            filename = self._extract_filename(response.headers.get('Content-Disposition', ''))
            content_type = response.headers.get('Content-Type', 'application/octet-stream')

            click.echo(f"  Content-Type: {content_type}", fg='green')
            click.echo(f"  Filename: {filename}", fg='green')

            return response.content.decode('utf-8', errors='ignore')
                
        except requests.RequestException as e:
            click.echo(f"  REST API request failed: {e}", err=True, fg='red')
            return None
    
    def _extract_filename(self, content_disposition: str) -> str:
        """Extract filename from Content header"""
        if not content_disposition:
            return "unknown_file"
        
        parts = content_disposition.split(';')
        for part in parts:
            part = part.strip()
            if part.startswith('filename='):
                filename = part.split('=', 1)[1].strip()
                if filename.startswith('"') and filename.endswith('"'):
                    filename = filename[1:-1]
                return filename
        
        return "unknown_file"