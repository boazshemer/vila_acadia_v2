"""
Unit tests for Pydantic models.
"""
import pytest
from pydantic import ValidationError
from src.backend.models import (
    AuthRequest, AuthResponse, HealthResponse,
    HoursSubmissionRequest, HoursSubmissionResponse,
    DailyTipRequest, DailyTipResponse
)


class TestAuthRequest:
    """Tests for AuthRequest model."""
    
    def test_valid_auth_request(self):
        """Test creating valid auth request."""
        request = AuthRequest(name="John Doe", pin="1234")
        assert request.name == "John Doe"
        assert request.pin == "1234"
    
    def test_auth_request_pin_too_short(self):
        """Test auth request with short PIN."""
        with pytest.raises(ValidationError) as exc:
            AuthRequest(name="John Doe", pin="123")
        
        assert "pin" in str(exc.value).lower()
    
    def test_auth_request_pin_too_long(self):
        """Test auth request with long PIN."""
        with pytest.raises(ValidationError) as exc:
            AuthRequest(name="John Doe", pin="12345")
        
        assert "pin" in str(exc.value).lower()
    
    def test_auth_request_non_digit_pin(self):
        """Test auth request with non-digit PIN."""
        with pytest.raises(ValidationError) as exc:
            AuthRequest(name="John Doe", pin="abcd")
        
        assert "digit" in str(exc.value).lower()
    
    def test_auth_request_empty_name(self):
        """Test auth request with empty name."""
        with pytest.raises(ValidationError):
            AuthRequest(name="", pin="1234")


class TestAuthResponse:
    """Tests for AuthResponse model."""
    
    def test_valid_auth_response_success(self):
        """Test creating successful auth response."""
        response = AuthResponse(
            success=True,
            message="Authentication successful",
            employee_name="John Doe"
        )
        assert response.success is True
        assert response.employee_name == "John Doe"
    
    def test_valid_auth_response_failure(self):
        """Test creating failed auth response."""
        response = AuthResponse(
            success=False,
            message="Invalid credentials",
            employee_name=""
        )
        assert response.success is False
        assert response.employee_name == ""


class TestHoursSubmissionRequest:
    """Tests for HoursSubmissionRequest model."""
    
    def test_valid_hours_request(self):
        """Test creating valid hours submission request."""
        request = HoursSubmissionRequest(
            employee_name="John Doe",
            date="2026-01-28",
            start_time="09:00",
            end_time="17:00"
        )
        assert request.employee_name == "John Doe"
        assert request.date == "2026-01-28"
        assert request.start_time == "09:00"
        assert request.end_time == "17:00"
    
    def test_hours_request_invalid_date_format(self):
        """Test hours request with invalid date format."""
        with pytest.raises(ValidationError) as exc:
            HoursSubmissionRequest(
                employee_name="John Doe",
                date="28-01-2026",  # Wrong format
                start_time="09:00",
                end_time="17:00"
            )
        
        assert "YYYY-MM-DD" in str(exc.value)
    
    def test_hours_request_invalid_time_format(self):
        """Test hours request with invalid time format."""
        with pytest.raises(ValidationError) as exc:
            HoursSubmissionRequest(
                employee_name="John Doe",
                date="2026-01-28",
                start_time="25:00",  # Invalid hour
                end_time="17:00"
            )
        
        assert "HH:MM" in str(exc.value) or "hour" in str(exc.value).lower()
    
    def test_hours_request_invalid_hour(self):
        """Test hours request with invalid hour."""
        with pytest.raises(ValidationError):
            HoursSubmissionRequest(
                employee_name="John Doe",
                date="2026-01-28",
                start_time="25:00",  # Invalid hour
                end_time="17:00"
            )
    
    def test_hours_request_invalid_minute(self):
        """Test hours request with invalid minute."""
        with pytest.raises(ValidationError):
            HoursSubmissionRequest(
                employee_name="John Doe",
                date="2026-01-28",
                start_time="09:00",
                end_time="17:60"  # Invalid minute
            )


class TestHoursSubmissionResponse:
    """Tests for HoursSubmissionResponse model."""
    
    def test_valid_hours_response(self):
        """Test creating valid hours submission response."""
        response = HoursSubmissionResponse(
            success=True,
            message="Hours submitted successfully",
            hours_worked=8.0,
            date="2026-01-28"
        )
        assert response.success is True
        assert response.hours_worked == 8.0
        assert response.date == "2026-01-28"


class TestDailyTipRequest:
    """Tests for DailyTipRequest model."""
    
    def test_valid_tip_request(self):
        """Test creating valid daily tip request."""
        request = DailyTipRequest(
            date="2026-01-28",
            total_tips=500.00
        )
        assert request.date == "2026-01-28"
        assert request.total_tips == 500.00
    
    def test_tip_request_negative_amount(self):
        """Test tip request with negative amount."""
        with pytest.raises(ValidationError) as exc:
            DailyTipRequest(
                date="2026-01-28",
                total_tips=-100.00
            )
        
        assert "greater than 0" in str(exc.value).lower()
    
    def test_tip_request_zero_amount(self):
        """Test tip request with zero amount."""
        with pytest.raises(ValidationError) as exc:
            DailyTipRequest(
                date="2026-01-28",
                total_tips=0.00
            )
        
        assert "greater than 0" in str(exc.value).lower()
    
    def test_tip_request_invalid_date(self):
        """Test tip request with invalid date."""
        with pytest.raises(ValidationError) as exc:
            DailyTipRequest(
                date="invalid-date",
                total_tips=500.00
            )
        
        assert "YYYY-MM-DD" in str(exc.value)


class TestDailyTipResponse:
    """Tests for DailyTipResponse model."""
    
    def test_valid_tip_response(self):
        """Test creating valid daily tip response."""
        response = DailyTipResponse(
            success=True,
            message="Tips submitted successfully",
            date="2026-01-28",
            total_tips=500.00,
            formulas_injected=True
        )
        assert response.success is True
        assert response.total_tips == 500.00
        assert response.formulas_injected is True


class TestHealthResponse:
    """Tests for HealthResponse model."""
    
    def test_valid_health_response(self):
        """Test creating valid health response."""
        response = HealthResponse(
            status="connected",
            spreadsheet_id="test_id",
            spreadsheet_title="Test Sheet",
            message="Successfully connected"
        )
        assert response.status == "connected"
        assert response.spreadsheet_id == "test_id"
        assert response.spreadsheet_title == "Test Sheet"

