"""
Simple test to verify test infrastructure is working.
Run this first to ensure everything is set up correctly.
"""
import pytest


def test_pytest_working():
    """Verify pytest is working."""
    assert True


def test_basic_math():
    """Verify basic assertions work."""
    assert 1 + 1 == 2
    assert 2 * 3 == 6


def test_string_operations():
    """Verify string operations work."""
    assert "hello".upper() == "HELLO"
    assert "world" in "hello world"


class TestBasicFixtures:
    """Test that basic fixtures work."""
    
    def test_with_fixture(self, mock_settings_data):
        """Test that fixtures from conftest.py work."""
        assert isinstance(mock_settings_data, list)
        assert len(mock_settings_data) == 3
        assert mock_settings_data[0]["name"] == "John Doe"


def test_imports():
    """Verify we can import our modules."""
    from src.backend import models
    from src.backend import config
    
    # Verify models exist
    assert hasattr(models, 'AuthRequest')
    assert hasattr(models, 'AuthResponse')
    
    # Verify config is set up
    assert config.settings is not None


if __name__ == "__main__":
    # Allow running this file directly
    pytest.main([__file__, "-v"])

