"""
Integration tests for FastAPI endpoints.
"""
import pytest
from unittest.mock import patch, MagicMock


class TestRootEndpoint:
    """Tests for the root endpoint."""
    
    def test_root_returns_service_info(self, test_client):
        """Test that root endpoint returns API information."""
        response = test_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Vila Acadia Timesheet API"
        assert data["version"] == "1.0.0"
        assert data["status"] == "running"
        assert "endpoints" in data


class TestHealthEndpoint:
    """Tests for the health check endpoint."""
    
    def test_health_check_success(self, test_client, mock_gsheets_service):
        """Test successful health check."""
        with patch.object(mock_gsheets_service, 'health_check') as mock_health:
            mock_health.return_value = {
                "status": "connected",
                "spreadsheet_id": "test_sheet_id",
                "spreadsheet_title": "Test Sheet",
                "message": "Successfully connected"
            }
            
            response = test_client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "connected"
            assert data["spreadsheet_title"] == "Test Sheet"
    
    def test_health_check_failure(self, test_client, mock_gsheets_service):
        """Test health check when connection fails."""
        with patch.object(mock_gsheets_service, 'health_check') as mock_health:
            mock_health.return_value = {
                "status": "error",
                "spreadsheet_id": "test_sheet_id",
                "message": "Failed to connect"
            }
            
            response = test_client.get("/health")
            
            assert response.status_code == 503
            assert "Failed to connect" in response.json()["detail"]


class TestAuthEndpoint:
    """Tests for authentication endpoint."""
    
    def test_auth_success(self, test_client, mock_gsheets_service):
        """Test successful authentication."""
        with patch.object(mock_gsheets_service, 'verify_employee_pin') as mock_verify:
            mock_verify.return_value = True
            
            response = test_client.post("/auth/verify", json={
                "name": "John Doe",
                "pin": "1234"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "Authentication successful"
            assert data["employee_name"] == "John Doe"
    
    def test_auth_failure_wrong_pin(self, test_client, mock_gsheets_service):
        """Test authentication with wrong PIN."""
        with patch.object(mock_gsheets_service, 'verify_employee_pin') as mock_verify:
            mock_verify.return_value = False
            
            response = test_client.post("/auth/verify", json={
                "name": "John Doe",
                "pin": "0000"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is False
            assert "Invalid credentials" in data["message"]
    
    def test_auth_invalid_pin_format(self, test_client):
        """Test authentication with invalid PIN format."""
        response = test_client.post("/auth/verify", json={
            "name": "John Doe",
            "pin": "12"  # Too short
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_auth_non_digit_pin(self, test_client):
        """Test authentication with non-digit PIN."""
        response = test_client.post("/auth/verify", json={
            "name": "John Doe",
            "pin": "abcd"
        })
        
        assert response.status_code == 422  # Validation error


class TestHoursSubmissionEndpoint:
    """Tests for hours submission endpoint."""
    
    def test_submit_hours_success(self, test_client, mock_gsheets_service, sample_hours_request):
        """Test successful hours submission."""
        with patch.object(mock_gsheets_service, 'is_month_closed') as mock_closed, \
             patch.object(mock_gsheets_service, 'calculate_hours') as mock_calc, \
             patch.object(mock_gsheets_service, 'submit_hours') as mock_submit:
            
            mock_closed.return_value = False
            mock_calc.return_value = 8.0
            mock_submit.return_value = {
                "row": 2,
                "column": 3,
                "hours": 8.0,
                "column_created": True
            }
            
            response = test_client.post("/submit-hours", json=sample_hours_request)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["hours_worked"] == 8.0
            assert "New column created" in data["message"]
    
    def test_submit_hours_month_closed(self, test_client, mock_gsheets_service, sample_hours_request):
        """Test hours submission when month is closed."""
        with patch.object(mock_gsheets_service, 'is_month_closed') as mock_closed:
            mock_closed.return_value = True
            
            response = test_client.post("/submit-hours", json=sample_hours_request)
            
            assert response.status_code == 400
            assert "closed" in response.json()["detail"].lower()
    
    def test_submit_hours_employee_not_found(self, test_client, mock_gsheets_service):
        """Test hours submission for non-existent employee."""
        with patch.object(mock_gsheets_service, 'is_month_closed') as mock_closed, \
             patch.object(mock_gsheets_service, 'get_employee_settings') as mock_settings:
            
            mock_closed.return_value = False
            mock_settings.return_value = [{"name": "Other Person", "pin": "1111"}]
            
            response = test_client.post("/submit-hours", json={
                "employee_name": "Unknown Person",
                "date": "2026-01-28",
                "start_time": "09:00",
                "end_time": "17:00"
            })
            
            assert response.status_code == 404
            assert "not found" in response.json()["detail"]
    
    def test_submit_hours_invalid_date_format(self, test_client):
        """Test hours submission with invalid date format."""
        response = test_client.post("/submit-hours", json={
            "employee_name": "John Doe",
            "date": "28-01-2026",  # Wrong format
            "start_time": "09:00",
            "end_time": "17:00"
        })
        
        assert response.status_code == 422
    
    def test_submit_hours_invalid_time_format(self, test_client):
        """Test hours submission with invalid time format."""
        response = test_client.post("/submit-hours", json={
            "employee_name": "John Doe",
            "date": "2026-01-28",
            "start_time": "25:00",  # Invalid hour
            "end_time": "17:00"
        })
        
        assert response.status_code == 422


class TestDailyTipEndpoint:
    """Tests for manager daily tip submission endpoint."""
    
    def test_submit_daily_tip_success(self, test_client, mock_gsheets_service, sample_tip_request):
        """Test successful daily tip submission."""
        with patch.object(mock_gsheets_service, 'is_month_closed') as mock_closed, \
             patch.object(mock_gsheets_service, 'submit_daily_tips') as mock_submit:
            
            mock_closed.return_value = False
            mock_submit.return_value = {
                "column": 3,
                "total_tips": 500.00,
                "employee_count": 5,
                "formulas_injected": True
            }
            
            response = test_client.post("/manager/submit-daily-tip", json=sample_tip_request)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["total_tips"] == 500.00
            assert data["formulas_injected"] is True
            assert "5 employees" in data["message"]
    
    def test_submit_daily_tip_month_closed(self, test_client, mock_gsheets_service, sample_tip_request):
        """Test daily tip submission when month is closed."""
        with patch.object(mock_gsheets_service, 'is_month_closed') as mock_closed:
            mock_closed.return_value = True
            
            response = test_client.post("/manager/submit-daily-tip", json=sample_tip_request)
            
            assert response.status_code == 400
            assert "closed" in response.json()["detail"].lower()
    
    def test_submit_daily_tip_negative_amount(self, test_client):
        """Test daily tip submission with negative amount."""
        response = test_client.post("/manager/submit-daily-tip", json={
            "date": "2026-01-28",
            "total_tips": -100.00
        })
        
        assert response.status_code == 422
    
    def test_submit_daily_tip_zero_amount(self, test_client):
        """Test daily tip submission with zero amount."""
        response = test_client.post("/manager/submit-daily-tip", json={
            "date": "2026-01-28",
            "total_tips": 0.00
        })
        
        assert response.status_code == 422
    
    def test_submit_daily_tip_invalid_date(self, test_client):
        """Test daily tip submission with invalid date."""
        response = test_client.post("/manager/submit-daily-tip", json={
            "date": "invalid-date",
            "total_tips": 500.00
        })
        
        assert response.status_code == 422

