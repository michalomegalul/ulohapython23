import pytest
import uuid
import json
import tempfile
import os
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from cli.commands import cli
from cli.rest_client import RestAPIClient
from cli.grpc_client import GrpcAPIClient
from cli.database import DatabaseManager


class TestRestAPIClient:
    """Test REST API client functionality"""
    
    def setup_method(self):
        self.client = RestAPIClient()
        self.test_uuid = str(uuid.uuid4())
    
    def test_uuid_validation(self):
        """Test UUID validation"""
        assert self.client.validate_uuid(self.test_uuid) is True
        assert self.client.validate_uuid("invalid-uuid") is False
        assert self.client.validate_uuid("") is False
    
    def test_parse_json_content(self):
        """Test JSON content parsing"""
        json_content = json.dumps({
            "domains": [
                {
                    "fqdn": "test-json.com",
                    "registered_at": "2025-08-24 13:29:27+00",
                    "unregistered_at": None
                },
                {
                    "fqdn": "expired-json.org",
                    "registered_at": "2023-01-01 00:00:00+00",
                    "unregistered_at": "2024-01-01 00:00:00+00"
                }
            ],
            "flags": [
                {
                    "domain_fqdn": "expired-json.org",
                    "flag": "EXPIRED",
                    "valid_from": "2024-01-01 00:00:00+00",
                    "valid_to": None
                }
            ]
        })
        
        metadata = {
            "name": "domains.json",
            "mimetype": "application/json",
            "size": len(json_content)
        }
        
        result = self.client._parse_json_content(json_content, metadata, self.test_uuid)
        
        assert result["source"] == "REST_API"
        assert len(result["domains"]) == 2
        assert len(result["flags"]) == 1
        assert result["domains"][0]["fqdn"] == "test-json.com"
        assert result["flags"][0]["flag"] == "EXPIRED"
    
    def test_parse_csv_content(self):
        """Test CSV content parsing"""
        csv_content = """fqdn,registered_at,unregistered_at
test-csv.com,2025-08-24 13:29:27+00,
expired-csv.org,2023-01-01 00:00:00+00,2024-01-01 00:00:00+00
active-csv.net,2024-01-01 00:00:00+00,"""
        
        metadata = {
            "name": "domains.csv",
            "mimetype": "text/csv",
            "size": len(csv_content)
        }
        
        result = self.client._parse_csv_content(csv_content, metadata, self.test_uuid)
        
        assert result["source"] == "REST_API"
        assert len(result["domains"]) == 3
        assert result["domains"][0]["fqdn"] == "test-csv.com"
        assert result["domains"][1]["unregistered_at"] == "2024-01-01 00:00:00+00"
    
    def test_parse_text_content(self):
        """Test plain text content parsing"""
        text_content = """example.com
test.org
# This is a comment
active-domain.net
another-test.com"""
        
        metadata = {
            "name": "domains.txt",
            "mimetype": "text/plain",
            "size": len(text_content)
        }
        
        result = self.client._parse_text_content(text_content, metadata, self.test_uuid)
        
        assert result["source"] == "REST_API"
        assert len(result["domains"]) == 4  # Should skip comment
        assert result["domains"][0]["fqdn"] == "example.com"
        assert result["domains"][2]["fqdn"] == "active-domain.net"
    
    def test_extract_filename(self):
        """Test filename extraction from Content-Disposition"""
        # Test with quotes
        header1 = 'attachment; filename="test.json"'
        assert self.client._extract_filename(header1) == "test.json"
        
        # Test without quotes
        header2 = 'attachment; filename=test.csv'
        assert self.client._extract_filename(header2) == "test.csv"
        
        # Test empty header
        assert self.client._extract_filename("") == "unknown_file"


class TestGrpcAPIClient:
    """Test gRPC API client functionality"""
    
    def setup_method(self):
        self.client = GrpcAPIClient()
        self.test_uuid = str(uuid.uuid4())
    
    def test_uuid_validation(self):
        """Test UUID validation"""
        assert self.client.validate_uuid(self.test_uuid) is True
        assert self.client.validate_uuid("invalid-uuid") is False


class TestCLI:
    """Test CLI commands"""
    
    def setup_method(self):
        self.runner = CliRunner()
    
    def test_cli_help(self):
        """Test CLI help command"""
        result = self.runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert 'Domain Management CLI Tool' in result.output
        assert 'michalomegalul' in result.output
    
    def test_status_command(self):
        """Test status command"""
        with patch.dict(os.environ, {
            'APP_VERSION': '1.0.0',
            'APP_AUTHOR': 'michalomegalul',
            'API_BASE_URL': 'http://test-api:8000'
        }):
            with patch('cli.database.DatabaseManager.get_system_stats') as mock_stats:
                mock_stats.return_value = {
                    'total_domains': 10,
                    'active_domains': 8,
                    'total_flags': 5,
                    'active_flags': 2
                }
                
                result = self.runner.invoke(cli, ['status'])
                
                assert 'michalomegalul' in result.output
                assert '1.0.0' in result.output
                assert 'http://test-api:8000' in result.output
    
    def test_fetch_domains_invalid_uuid(self):
        """Test fetch-domains with invalid UUID"""
        result = self.runner.invoke(cli, ['fetch-domains', '--uuid', 'invalid'])
        
        assert result.exit_code != 0
        assert 'Invalid UUID format' in result.output
    
    @patch('cli.rest_client.RestAPIClient.fetch_domains')
    @patch('cli.database.DatabaseManager.store_domains')
    def test_fetch_domains_success(self, mock_store, mock_fetch):
        """Test successful domain fetching"""
        test_uuid = str(uuid.uuid4())
        
        # Mock API response
        mock_fetch.return_value = {
            "source": "REST_API",
            "uuid": test_uuid,
            "domains": [{"fqdn": "test.com", "registered_at": "2025-08-24 13:29:27+00"}],
            "flags": []
        }
        mock_store.return_value = 1
        
        result = self.runner.invoke(cli, ['fetch-domains', '--uuid', test_uuid])
        
        assert result.exit_code == 0
        assert 'stored 1 new domains' in result.output


class TestDatabaseManager:
    """Test database operations"""
    
    @patch('cli.database.psycopg2.connect')
    def test_store_domains(self, mock_connect):
        """Test domain storage"""
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 1
        
        db = DatabaseManager()
        
        test_data = {
            "domains": [
                {
                    "fqdn": "test.com",
                    "registered_at": "2025-08-24 13:29:27+00",
                    "unregistered_at": None
                }
            ],
            "flags": []
        }
        
        with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test:test@localhost/test'}):
            result = db.store_domains(test_data)
            
            assert result == 1
            mock_cursor.execute.assert_called()


# Integration Tests
class TestIntegration:
    """Integration tests with real data"""
    
    def test_end_to_end_json_processing(self):
        """Test complete JSON file processing"""
        client = RestAPIClient()
        
        test_data = {
            "domains": [
                {
                    "fqdn": "integration-test.com",
                    "registered_at": "2025-08-24 13:29:27+00",
                    "unregistered_at": None
                }
            ],
            "flags": [
                {
                    "domain_fqdn": "integration-test.com",
                    "flag": "EXPIRED",
                    "valid_from": "2025-08-24 13:29:27+00",
                    "valid_to": None
                }
            ]
        }
        
        json_content = json.dumps(test_data)
        metadata = {
            "name": "test.json",
            "mimetype": "application/json",
            "size": len(json_content)
        }
        
        result = client._parse_file_content(json_content, metadata, str(uuid.uuid4()))
        
        assert result["source"] == "REST_API"
        assert len(result["domains"]) == 1
        assert len(result["flags"]) == 1
        assert result["domains"][0]["fqdn"] == "integration-test.com"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])