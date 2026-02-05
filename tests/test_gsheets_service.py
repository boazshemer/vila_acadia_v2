"""
Unit tests for Google Sheets service.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch
from src.backend.gsheets_service import GoogleSheetsService
import gspread


class TestGoogleSheetsService:
    """Tests for GoogleSheetsService class."""
    
    @pytest.fixture
    def service(self):
        """Create a fresh service instance."""
        return GoogleSheetsService()
    
    def test_initialization(self, service):
        """Test service initialization."""
        assert service._client is None
        assert service._spreadsheet is None
        assert service.SETTINGS_TAB == "Settings"
    
    def test_health_check_success(self, service, mock_spreadsheet):
        """Test successful health check."""
        service._spreadsheet = mock_spreadsheet
        
        result = service.health_check()
        
        assert result["status"] == "connected"
        assert "Successfully connected" in result["message"]
    
    def test_health_check_failure(self, service):
        """Test health check when connection fails."""
        service._spreadsheet = None
        service._client = None
        
        with patch.object(service, 'get_spreadsheet', side_effect=Exception("Connection failed")):
            result = service.health_check()
            
            assert result["status"] == "error"
            assert "Failed to connect" in result["message"]


class TestEmployeeSettings:
    """Tests for employee settings methods."""
    
    @pytest.fixture
    def service(self, mock_spreadsheet):
        """Create service with mocked spreadsheet."""
        svc = GoogleSheetsService()
        svc._spreadsheet = mock_spreadsheet
        return svc
    
    def test_get_employee_settings_success(self, service, mock_spreadsheet):
        """Test getting employee settings."""
        mock_worksheet = MagicMock()
        mock_worksheet.get_all_records.return_value = [
            {"Name": "John Doe", "PIN": "1234"},
            {"Name": "Jane Smith", "PIN": "5678"}
        ]
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        
        employees = service.get_employee_settings()
        
        assert len(employees) == 2
        assert employees[0]["name"] == "John Doe"
        assert employees[0]["pin"] == "1234"
    
    def test_get_employee_settings_lowercase_headers(self, service, mock_spreadsheet):
        """Test getting settings with lowercase headers."""
        mock_worksheet = MagicMock()
        mock_worksheet.get_all_records.return_value = [
            {"name": "Bob Johnson", "pin": "9999"}
        ]
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        
        employees = service.get_employee_settings()
        
        assert len(employees) == 1
        assert employees[0]["name"] == "Bob Johnson"
    
    def test_get_employee_settings_missing_tab(self, service, mock_spreadsheet):
        """Test error when Settings tab doesn't exist."""
        mock_spreadsheet.worksheet.side_effect = gspread.WorksheetNotFound("Not found")
        
        with pytest.raises(Exception) as exc:
            service.get_employee_settings()
        
        assert "Settings" in str(exc.value)
    
    def test_verify_employee_pin_success(self, service, mock_spreadsheet):
        """Test successful PIN verification."""
        mock_worksheet = MagicMock()
        mock_worksheet.get_all_records.return_value = [
            {"Name": "John Doe", "PIN": "1234"}
        ]
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        
        result = service.verify_employee_pin("John Doe", "1234")
        
        assert result is True
    
    def test_verify_employee_pin_case_insensitive(self, service, mock_spreadsheet):
        """Test PIN verification is case-insensitive for names."""
        mock_worksheet = MagicMock()
        mock_worksheet.get_all_records.return_value = [
            {"Name": "John Doe", "PIN": "1234"}
        ]
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        
        result = service.verify_employee_pin("JOHN DOE", "1234")
        
        assert result is True
    
    def test_verify_employee_pin_wrong_pin(self, service, mock_spreadsheet):
        """Test PIN verification with wrong PIN."""
        mock_worksheet = MagicMock()
        mock_worksheet.get_all_records.return_value = [
            {"Name": "John Doe", "PIN": "1234"}
        ]
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        
        result = service.verify_employee_pin("John Doe", "0000")
        
        assert result is False
    
    def test_verify_employee_pin_unknown_employee(self, service, mock_spreadsheet):
        """Test PIN verification for unknown employee."""
        mock_worksheet = MagicMock()
        mock_worksheet.get_all_records.return_value = [
            {"Name": "John Doe", "PIN": "1234"}
        ]
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        
        result = service.verify_employee_pin("Unknown Person", "1234")
        
        assert result is False


class TestTimeCalculations:
    """Tests for time calculation methods."""
    
    @pytest.fixture
    def service(self):
        """Create service instance."""
        return GoogleSheetsService()
    
    def test_calculate_hours_normal_shift(self, service):
        """Test calculating hours for normal shift."""
        hours = service.calculate_hours("09:00", "17:00")
        assert hours == 8.0
    
    def test_calculate_hours_half_hour(self, service):
        """Test calculating hours with half hours."""
        hours = service.calculate_hours("09:00", "17:30")
        assert hours == 8.5
    
    def test_calculate_hours_overnight_shift(self, service):
        """Test calculating hours for overnight shift."""
        hours = service.calculate_hours("23:00", "02:00")
        assert hours == 3.0
    
    def test_calculate_hours_full_day(self, service):
        """Test calculating hours for full 24-hour shift."""
        hours = service.calculate_hours("00:00", "00:00")
        assert hours == 24.0
    
    def test_calculate_hours_one_minute(self, service):
        """Test calculating hours for 1 minute."""
        hours = service.calculate_hours("09:00", "09:01")
        assert hours == 0.02  # Rounded to 2 decimals


class TestMonthClosure:
    """Tests for month closure validation."""
    
    @pytest.fixture
    def service(self):
        """Create service instance."""
        return GoogleSheetsService()
    
    def test_is_month_closed_current_month(self, service):
        """Test that current month is not closed."""
        today = datetime.now()
        date_str = today.strftime("%Y-%m-%d")
        
        result = service.is_month_closed(date_str)
        
        # Current month should not be closed if before cutoff
        if today.day <= 2:
            # If today is 1st or 2nd of month, last month might be closed
            pass
        else:
            assert result is False
    
    def test_is_month_closed_old_month(self, service):
        """Test that old months are closed."""
        # Date from 3 months ago
        old_date = datetime.now() - timedelta(days=90)
        date_str = old_date.strftime("%Y-%m-%d")
        
        result = service.is_month_closed(date_str)
        
        assert result is True
    
    def test_is_month_closed_cutoff_boundary(self, service):
        """Test month closure on cutoff boundary."""
        # Get a date from last month
        today = datetime.now()
        if today.month == 1:
            last_month = datetime(today.year - 1, 12, 15)
        else:
            last_month = datetime(today.year, today.month - 1, 15)
        
        date_str = last_month.strftime("%Y-%m-%d")
        result = service.is_month_closed(date_str)
        
        # If today is after the 2nd of this month, last month is closed
        if today.day > 2:
            assert result is True


class TestColumnHelpers:
    """Tests for column helper methods."""
    
    @pytest.fixture
    def service(self):
        """Create service instance."""
        return GoogleSheetsService()
    
    def test_col_index_to_letter_single(self, service):
        """Test converting single-digit column indices."""
        assert service._col_index_to_letter(1) == "A"
        assert service._col_index_to_letter(2) == "B"
        assert service._col_index_to_letter(26) == "Z"
    
    def test_col_index_to_letter_double(self, service):
        """Test converting double-digit column indices."""
        assert service._col_index_to_letter(27) == "AA"
        assert service._col_index_to_letter(28) == "AB"
        assert service._col_index_to_letter(52) == "AZ"
    
    def test_col_index_to_letter_triple(self, service):
        """Test converting triple-digit column indices."""
        assert service._col_index_to_letter(703) == "AAA"


class TestGetOrCreateDateColumn:
    """Tests for date column management."""
    
    @pytest.fixture
    def service(self):
        """Create service instance."""
        return GoogleSheetsService()
    
    def test_get_existing_date_column(self, service, mock_worksheet):
        """Test getting existing date column."""
        mock_worksheet.row_values.return_value = ["Employee", "01/28/2026", "01/29/2026"]
        
        col_idx, was_created = service.get_or_create_date_column("2026-01-28", mock_worksheet)
        
        assert col_idx == 2
        assert was_created is False
    
    def test_create_new_date_column(self, service, mock_worksheet):
        """Test creating new date column."""
        mock_worksheet.row_values.return_value = ["Employee", "01/28/2026"]
        
        col_idx, was_created = service.get_or_create_date_column("2026-01-29", mock_worksheet)
        
        assert col_idx == 3
        assert was_created is True
        mock_worksheet.update_cell.assert_called_once()


class TestEmployeeRowManagement:
    """Tests for employee row management."""
    
    @pytest.fixture
    def service(self):
        """Create service instance."""
        return GoogleSheetsService()
    
    def test_get_existing_employee_row(self, service, mock_worksheet):
        """Test finding existing employee row."""
        mock_worksheet.col_values.return_value = ["Employee", "John Doe", "Jane Smith"]
        
        row = service.get_employee_row("John Doe", mock_worksheet)
        
        assert row == 2
    
    def test_get_employee_row_case_insensitive(self, service, mock_worksheet):
        """Test finding employee row case-insensitively."""
        mock_worksheet.col_values.return_value = ["Employee", "John Doe", "Jane Smith"]
        
        row = service.get_employee_row("JOHN DOE", mock_worksheet)
        
        assert row == 2
    
    def test_get_employee_row_not_found(self, service, mock_worksheet):
        """Test employee not found."""
        mock_worksheet.col_values.return_value = ["Employee", "John Doe"]
        
        row = service.get_employee_row("Unknown Person", mock_worksheet)
        
        assert row is None
    
    def test_get_or_create_employee_row_existing(self, service, mock_worksheet):
        """Test getting existing employee row."""
        mock_worksheet.col_values.return_value = ["Employee", "John Doe"]
        
        row = service.get_or_create_employee_row("John Doe", mock_worksheet)
        
        assert row == 2
        mock_worksheet.update_cell.assert_not_called()
    
    def test_get_or_create_employee_row_new(self, service, mock_worksheet):
        """Test creating new employee row."""
        mock_worksheet.col_values.return_value = ["Employee", "John Doe"]
        
        row = service.get_or_create_employee_row("Jane Smith", mock_worksheet)
        
        assert row == 3
        mock_worksheet.update_cell.assert_called_once_with(3, 1, "Jane Smith")

