import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from cli import cli


class TestFileClient:
    """Test file client functionality as per assignment requirements"""
    
    def setup_method(self):
        self.runner = CliRunner()
    
    def test_file_client_help(self):
        """Test file-client help command"""
        result = self.runner.invoke(cli, ['file-client', '--help'])
        
        assert result.exit_code == 0
        assert 'File client for REST/gRPC operations' in result.output
        assert 'stat' in result.output
        assert 'read' in result.output
    
    @patch('cli.requests.get')
    def test_file_client_stat_rest_success(self, mock_get):
        """Test successful stat command with REST backend"""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'name': 'test.txt',
            'size': 1234,
            'mimetype': 'text/plain',
            'create_datetime': '2025-08-25T09:16:09Z'
        }
        mock_get.return_value = mock_response
        
        result = self.runner.invoke(cli, [
            'file-client',
            '--backend', 'rest',
            '--base-url', 'http://test-api/',
            'stat', 
            '123e4567-e89b-12d3-a456-426614174000'
        ])
        
        assert result.exit_code == 0
        assert 'Name: test.txt' in result.output
        assert '1234 bytes' in result.output
        assert 'text/plain' in result.output
    
    @patch('cli.requests.get')
    def test_file_client_stat_rest_not_found(self, mock_get):
        """Test stat command when file not found"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = self.runner.invoke(cli, [
            'file-client',
            '--backend', 'rest',
            'stat', 
            '123e4567-e89b-12d3-a456-426614174000'
        ])
        
        assert result.exit_code == 1
        assert 'File not found' in result.output
    
    @patch('cli.requests.get')
    def test_file_client_read_rest_success(self, mock_get):
        """Test successful read command with REST backend"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = 'Hello, world!'
        mock_response.content = b'Hello, world!'
        mock_get.return_value = mock_response
        
        result = self.runner.invoke(cli, [
            'file-client',
            '--backend', 'rest',
            'read', 
            '123e4567-e89b-12d3-a456-426614174000'
        ])
        
        assert result.exit_code == 0
        assert 'Hello, world!' in result.output
    
    def test_file_client_grpc_not_implemented(self):
        """Test that gRPC shows not implemented message"""
        result = self.runner.invoke(cli, [
            'file-client',
            '--backend', 'grpc',
            'stat', 
            '123e4567-e89b-12d3-a456-426614174000'
        ])
        
        assert result.exit_code == 1
        assert 'gRPC backend not implemented' in result.output
    
    def test_file_client_invalid_uuid(self):
        """Test file client with invalid UUID"""
        result = self.runner.invoke(cli, [
            'file-client',
            'stat',
            'invalid-uuid'
        ])
        
        assert result.exit_code == 1
        assert 'Invalid UUID' in result.output
    
    def test_file_client_default_backend_is_grpc(self):
        """Test that default backend is gRPC as per spec"""
        result = self.runner.invoke(cli, [
            'file-client',
            'stat',
            '123e4567-e89b-12d3-a456-426614174000'
        ])
        
        # Should fail with gRPC not implemented (proving default is gRPC)
        assert result.exit_code == 1
        assert 'gRPC backend not implemented' in result.output


class TestDatabaseCommands:
    """Test database-related commands"""
    
    def setup_method(self):
        self.runner = CliRunner()
    
    @patch('cli.DatabaseManager')
    def test_status_command(self, mock_db):
        """Test status command"""
        mock_instance = mock_db.return_value
        mock_instance.get_stats.return_value = {
            'total_domains': 5,
            'active_domains': 3,
            'total_flags': 2
        }
        
        result = self.runner.invoke(cli, ['status'])
        assert result.exit_code == 0
        assert 'Database connected' in result.output
        assert '5 total' in result.output
        assert '3 active' in result.output


if __name__ == '__main__':
    pytest.main([__file__, '-v'])