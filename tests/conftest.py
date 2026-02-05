"""
Pytest configuration and shared fixtures.
"""
import pytest
import os
import json
from unittest.mock import Mock, MagicMock
from fastapi.testclient import TestClient
import gspread


# Set up test environment variables BEFORE any imports that need them
def pytest_configure(config):
    """Configure pytest and set up test environment."""
    # Set required environment variables for testing
    os.environ["GOOGLE_SHEET_ID"] = "test_sheet_id_12345"
    os.environ["SERVICE_ACCOUNT_JSON"] = json.dumps({
        "type": "service_account",
        "project_id": "test-project",
        "private_key": "test-key"
    })
    os.environ["HOST"] = "127.0.0.1"
    os.environ["PORT"] = "8000"
    
    # Reinitialize settings with test environment
    from src.backend import config
    config.settings = config.Settings()


@pytest.fixture
def mock_spreadsheet():
    """Create a mock Google Spreadsheet."""
    spreadsheet = MagicMock(spec=gspread.Spreadsheet)
    spreadsheet.title = "Vila Acadia Timesheet (Test)"
    return spreadsheet


@pytest.fixture
def mock_worksheet():
    """Create a mock Google Worksheet."""
    worksheet = MagicMock(spec=gspread.Worksheet)
    worksheet.title = "January 2026"
    return worksheet


@pytest.fixture
def mock_settings_data():
    """Mock employee settings data."""
    return [
        {"name": "John Doe", "pin": "1234"},
        {"name": "Jane Smith", "pin": "5678"},
        {"name": "Bob Johnson", "pin": "9999"}
    ]


@pytest.fixture
def mock_gsheets_service(monkeypatch, mock_spreadsheet, mock_worksheet, mock_settings_data):
    """Mock the Google Sheets service."""
    from src.backend.gsheets_service import gs_service
    
    # Mock the connection
    monkeypatch.setattr(gs_service, '_spreadsheet', mock_spreadsheet)
    monkeypatch.setattr(gs_service, '_client', MagicMock())
    
    # Mock get_employee_settings
    def mock_get_settings():
        return mock_settings_data
    
    monkeypatch.setattr(gs_service, 'get_employee_settings', mock_get_settings)
    
    # Mock get_or_create_month_sheet
    monkeypatch.setattr(gs_service, 'get_or_create_month_sheet', lambda date=None: mock_worksheet)
    
    return gs_service


@pytest.fixture
def test_client(mock_gsheets_service):
    """Create a test client for the FastAPI app."""
    from src.backend.main import app
    
    # Skip lifespan events during testing
    app.router.lifespan_context = None
    
    return TestClient(app)


@pytest.fixture
def sample_hours_request():
    """Sample hours submission request data."""
    return {
        "employee_name": "John Doe",
        "date": "2026-01-28",
        "start_time": "09:00",
        "end_time": "17:00"
    }


@pytest.fixture
def sample_tip_request():
    """Sample daily tip request data."""
    return {
        "date": "2026-01-28",
        "total_tips": 500.00
    }

