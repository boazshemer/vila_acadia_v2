"""
Unit tests for configuration management.
"""
import pytest
import json
from pydantic import ValidationError
from src.backend.config import Settings


class TestSettings:
    """Tests for Settings configuration."""
    
    def test_valid_settings(self, monkeypatch):
        """Test creating valid settings."""
        service_account = {
            "type": "service_account",
            "project_id": "test-project",
            "private_key": "test-key"
        }
        
        monkeypatch.setenv("GOOGLE_SHEET_ID", "test_sheet_id")
        monkeypatch.setenv("SERVICE_ACCOUNT_JSON", json.dumps(service_account))
        
        settings = Settings()
        
        assert settings.google_sheet_id == "test_sheet_id"
        # Test environment sets HOST to 127.0.0.1
        assert settings.host == "127.0.0.1"
        assert settings.port == 8000
    
    def test_custom_host_port(self, monkeypatch):
        """Test custom host and port configuration."""
        service_account = {"type": "service_account"}
        
        monkeypatch.setenv("GOOGLE_SHEET_ID", "test_sheet_id")
        monkeypatch.setenv("SERVICE_ACCOUNT_JSON", json.dumps(service_account))
        monkeypatch.setenv("HOST", "127.0.0.1")
        monkeypatch.setenv("PORT", "3000")
        
        settings = Settings()
        
        assert settings.host == "127.0.0.1"
        assert settings.port == 3000
    
    def test_invalid_service_account_json(self, monkeypatch):
        """Test invalid service account JSON."""
        monkeypatch.setenv("GOOGLE_SHEET_ID", "test_sheet_id")
        monkeypatch.setenv("SERVICE_ACCOUNT_JSON", "not-valid-json")
        
        with pytest.raises(ValidationError) as exc:
            Settings()
        
        assert "valid JSON" in str(exc.value)
    
    def test_get_service_account_dict(self, monkeypatch):
        """Test getting service account as dictionary."""
        service_account = {
            "type": "service_account",
            "project_id": "test-project"
        }
        
        monkeypatch.setenv("GOOGLE_SHEET_ID", "test_sheet_id")
        monkeypatch.setenv("SERVICE_ACCOUNT_JSON", json.dumps(service_account))
        
        settings = Settings()
        result = settings.get_service_account_dict()
        
        assert isinstance(result, dict)
        assert result["type"] == "service_account"
        assert result["project_id"] == "test-project"

