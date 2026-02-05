"""
Google Sheets Service for Vila Acadia - Version 2
Implements the correct tip distribution matrix structure.
"""
import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from .config import settings


class GoogleSheetsService:
    """Service for interacting with Google Sheets as a database."""
    
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # Sheet configuration
    SETTINGS_TAB = "Settings"
    
    def __init__(self):
        """Initialize the Google Sheets service with authentication."""
        self._client: Optional[gspread.Client] = None
        self._spreadsheet: Optional[gspread.Spreadsheet] = None
    
    def _get_credentials(self) -> Credentials:
        """Create credentials from service account JSON."""
        try:
            return Credentials.from_service_account_file('service-account.json', scopes=self.SCOPES)
        except Exception:
            creds_dict = settings.get_service_account_dict()
            return Credentials.from_service_account_info(creds_dict, scopes=self.SCOPES)
    
    def connect(self) -> None:
        """Establish connection to Google Sheets."""
        if self._client is None:
            creds = self._get_credentials()
            self._client = gspread.authorize(creds)
            self._spreadsheet = self._client.open_by_key(settings.google_sheet_id)
    
    def get_spreadsheet(self) -> gspread.Spreadsheet:
        """Get the spreadsheet object, connecting if necessary."""
        if self._spreadsheet is None:
            self.connect()
        return self._spreadsheet
    
    def health_check(self) -> Dict[str, str]:
        """Verify connectivity to Google Sheets."""
        try:
            sheet = self.get_spreadsheet()
            return {
                "status": "connected",
                "spreadsheet_id": settings.google_sheet_id,
                "spreadsheet_title": sheet.title,
                "message": "Successfully connected to Google Sheets"
            }
        except Exception as e:
            return {
                "status": "error",
                "spreadsheet_id": settings.google_sheet_id,
                "message": f"Failed to connect: {str(e)}"
            }
    
    def get_employee_settings(self) -> List[Dict[str, str]]:
        """Fetch employee roster and PINs from the Settings tab."""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            sheet = self.get_spreadsheet()
            settings_worksheet = sheet.worksheet(self.SETTINGS_TAB)
            records = settings_worksheet.get_all_records()
            
            logger.info(f"📊 Read {len(records)} records from Settings sheet")
            logger.info(f"📊 Raw records: {records}")
            
            employees = []
            for idx, record in enumerate(records):
                logger.info(f"📊 Processing record {idx}: {record}")
                
                name = (record.get("Name") or record.get("name") or 
                       record.get("Employee Name") or record.get("employee name") or "").strip()
                pin = str(record.get("PIN") or record.get("pin") or 
                         record.get("Pin") or "").strip()
                
                logger.info(f"📊 Extracted - name: '{name}', pin: '{pin}'")
                
                if name and pin:
                    employees.append({"name": name, "pin": pin})
                    logger.info(f"✅ Added employee: name='{name}', pin='{pin}'")
                else:
                    logger.warning(f"⚠️ Skipped record - name: '{name}', pin: '{pin}'")
            
            logger.info(f"📊 Total employees found: {len(employees)}")
            logger.info(f"📊 Employees list: {employees}")
            
            return employees
        
        except gspread.WorksheetNotFound:
            raise Exception(f"'{self.SETTINGS_TAB}' tab not found in the spreadsheet")
        except Exception as e:
            raise Exception(f"Error reading employee settings: {str(e)}")
    
    def verify_employee_pin(self, name: str, pin: str) -> bool:
        """Verify an employee's PIN against the Settings sheet."""
        try:
            employees = self.get_employee_settings()
            
            for employee in employees:
                if employee["name"].lower() == name.lower() and employee["pin"] == pin:
                    return True
            
            return False
        
        except Exception:
            return False
    
    def get_or_create_month_sheet(self, date: Optional[datetime] = None) -> gspread.Worksheet:
        """
        Get or create a worksheet for the month.
        
        Structure:
        Row 1: Empty
        Row 2: C2="TOTAL TIP", D2=empty (manager input)
        Row 3: C3="TOTAL HOURS", D3==SUM(C6:C70)
        Row 4: C4="TIP PER HOUR", D4==IF(D3>0, D2/D3, 0)
        Row 5: B5="שם העובד", C5="HOURS", D5+= Dates
        Row 6+: Employee data
        
        Args:
            date: Date to determine month (defaults to current date)
        
        Returns:
            The worksheet for the specified month.
        """
        if date is None:
            date = datetime.now()
        
        # Format: "MM-YYYY" (e.g., "02-2026")
        sheet_name = date.strftime("%m-%Y")
        
        sheet = self.get_spreadsheet()
        
        try:
            # Try to get existing worksheet
            worksheet = sheet.worksheet(sheet_name)
            
            # Check if Dashboard exists (C2 should have "TOTAL TIP")
            c2_value = worksheet.cell(2, 3).value  # C2
            if not c2_value or c2_value != "TOTAL TIP":
                # Dashboard doesn't exist, initialize it
                self._initialize_dashboard(worksheet)
            
            return worksheet
        
        except gspread.WorksheetNotFound:
            # Create new monthly worksheet
            worksheet = sheet.add_worksheet(
                title=sheet_name,
                rows=100,
                cols=50  # A + B + C (hours) + 47 date columns
            )
            
            # Initialize Dashboard and Headers
            self._initialize_dashboard(worksheet)
            
            return worksheet
    
    def _initialize_dashboard(self, worksheet: gspread.Worksheet) -> None:
        """
        Initialize the Headers for a worksheet.
        Each date will have its own dashboard in columns (3 columns per date).
        """
        # Check if employee numbers already exist in Column A6
        a6_value = worksheet.cell(6, 1).value  # A6
        if not a6_value or a6_value != "1":
            # Add employee numbers in Column A (rows 6-75)
            employee_numbers = [[i] for i in range(1, 71)]  # 1 to 70
            worksheet.update('A6:A75', employee_numbers, value_input_option='USER_ENTERED')
        
        # Check if employee name header exists in Column B5
        b5_value = worksheet.cell(5, 2).value  # B5
        if not b5_value or b5_value != 'שם העובד':
            # Add employee name header in Column B5
            worksheet.update_cell(5, 2, 'שם העובד')  # B5
            
            # Format A5 and B5 with bold and light green background
            worksheet.format('A5:B5', {
                "textFormat": {"bold": True},
                "backgroundColor": {"red": 0.85, "green": 0.92, "blue": 0.83},
                "horizontalAlignment": "CENTER"
            })
        
        # Each date creates its own columns
        # Freeze Row 5 and Columns A, B only (2 columns frozen)
        worksheet.freeze(rows=5, cols=2)
    
    def _col_index_to_letter(self, col_index: int) -> str:
        """Convert column index (1-based) to letter (A, B, C, ...)."""
        result = ""
        while col_index > 0:
            col_index -= 1
            result = chr(col_index % 26 + ord('A')) + result
            col_index //= 26
        return result
    
    def get_or_create_employee_row(self, employee_name: str, worksheet: gspread.Worksheet) -> int:
        """
        Get or create row for a specific employee.
        Employees start from row 6.
        Employee names are stored in column B.
        
        Args:
            employee_name: Employee name
            worksheet: Worksheet to search
        
        Returns:
            Row index (1-based, starting from 6)
        """
        # Get all values from column B (employee names)
        col_b = worksheet.col_values(2)  # Column B
        
        # Search for employee (case-insensitive, skip header rows 1-5)
        for idx, name in enumerate(col_b, start=1):
            if idx > 5 and name.strip().lower() == employee_name.lower().strip():
                return idx
        
        # Employee not found, add to next row (minimum row 6, max row 75)
        next_row = len(col_b) + 1
        if next_row < 6:
            next_row = 6
        if next_row > 75:
            raise ValueError("Maximum number of employees (70) reached")
        
        worksheet.update_cell(next_row, 2, employee_name)  # Column B
        return next_row
    
    def get_or_create_date_column(self, date: str, worksheet: gspread.Worksheet) -> Tuple[int, bool]:
        """
        Get or create columns for a specific date.
        
        First date gets 3 columns: Labels + HOURS + Date
        Subsequent dates get 2 columns: HOURS + Date (share labels column)
        
        Args:
            date: Date string in YYYY-MM-DD format
            worksheet: Worksheet to search
        
        Returns:
            Tuple of (hours_column_index, was_created)
        """
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        date_formatted = date_obj.strftime("%d/%m/%Y")  # e.g., "03/02/2026"
        
        # Get row 5 (headers)
        row5 = worksheet.row_values(5)
        
        # Search for existing date column (looking for date in row 5)
        for idx, header in enumerate(row5, start=1):
            if idx >= 3 and header == date_formatted:
                # Found the date column, hours column is one before
                return idx - 1, False
        
        # All dates follow the same pattern - no distinction between first and subsequent dates
        
        # Date not found, create new columns
        next_col = len(row5) + 1
        if next_col < 3:
            next_col = 3  # Start from column C
        
        # All dates use 2 columns: Labels+HOURS and Values+Date
        hours_col = next_col
        date_col = next_col + 1
        
        hours_letter = self._col_index_to_letter(hours_col)
        date_letter = self._col_index_to_letter(date_col)
        
        # Every date gets Labels in rows 2-4 of HOURS column
        worksheet.update_cell(2, hours_col, 'TOTAL TIP')
        worksheet.update_cell(3, hours_col, 'TOTAL HOURS')
        worksheet.update_cell(4, hours_col, 'TIP PER HOUR')
        
        # === HOURS COLUMN ===
        # Row 5: "HOURS"
        worksheet.update_cell(5, hours_col, 'HOURS')
        
        # === DATE COLUMN ===
        # Row 2: Empty (for manager to input TOTAL TIP value)
        # Row 3: Formula =SUM(C6:C70) (sum hours from hours column)
        # Row 4: Formula =D2/D3 (tip per hour)
        # Row 5: Date
        
        worksheet.update([[f'=SUM({hours_letter}6:{hours_letter}70)']], f'{date_letter}3', value_input_option='USER_ENTERED')
        worksheet.update([[f'={date_letter}2/{date_letter}3']], f'{date_letter}4', value_input_option='USER_ENTERED')
        worksheet.update_cell(5, date_col, date_formatted)
        
        # Format headers (rows 2-5) - bold, light green background
        worksheet.format(f'{hours_letter}2:{date_letter}5', {
            "textFormat": {"bold": True},
            "backgroundColor": {"red": 0.85, "green": 0.92, "blue": 0.83},
            "horizontalAlignment": "CENTER"
        })
        
        # Format rows 2-4 of hours column (values with proper formatting)
        worksheet.format(f'{hours_letter}2', {
            "textFormat": {"bold": True},
            "backgroundColor": {"red": 0.85, "green": 0.92, "blue": 0.83},
            "horizontalAlignment": "CENTER",
            "numberFormat": {
                "type": "CURRENCY",
                "pattern": "#,##0 ₪"
            }
        })
        
        worksheet.format(f'{hours_letter}3', {
            "textFormat": {"bold": True},
            "backgroundColor": {"red": 0.85, "green": 0.92, "blue": 0.83},
            "horizontalAlignment": "CENTER",
            "numberFormat": {
                "type": "NUMBER",
                "pattern": "0.00"
            }
        })
        
        worksheet.format(f'{hours_letter}4', {
            "textFormat": {"bold": True},
            "backgroundColor": {"red": 0.85, "green": 0.92, "blue": 0.83},
            "horizontalAlignment": "CENTER",
            "numberFormat": {
                "type": "CURRENCY",
                "pattern": "#,##0.00 ₪"
            }
        })
        
        # Format date column row 2 (TOTAL TIP value - light orange for manager input)
        worksheet.format(f'{date_letter}2', {
            "textFormat": {"bold": True},
            "backgroundColor": {"red": 1.0, "green": 0.85, "blue": 0.7},  # Light orange
            "horizontalAlignment": "CENTER",
            "numberFormat": {
                "type": "CURRENCY",
                "pattern": "#,##0 ₪"
            }
        })
        
        # Format hours column (light yellow background + 2 decimals)
        worksheet.format(f'{hours_letter}6:{hours_letter}70', {
            "backgroundColor": {"red": 1.0, "green": 0.95, "blue": 0.8},
            "numberFormat": {
                "type": "NUMBER",
                "pattern": "0.00"
            }
        })
        
        # Add tips formulas for date column rows 6-70 (=C6*$D$4, =C7*$D$4, ...)
        # Formula: hours_column * TIP_PER_HOUR (which is in date_column row 4)
        formulas = []
        for row in range(6, 71):
            formulas.append([f'={hours_letter}{row}*${date_letter}$4'])
        
        # Batch update formulas
        worksheet.update(
            f'{date_letter}6:{date_letter}70',
            formulas,
            value_input_option='USER_ENTERED'
        )
        
        # Format tips column (currency with ₪ symbol, no decimals)
        worksheet.format(f'{date_letter}6:{date_letter}70', {
            "numberFormat": {
                "type": "CURRENCY",
                "pattern": "#,##0 ₪"
            }
        })
        
        # Add right border to date column for visual separation between date blocks
        worksheet.format(f'{date_letter}1:{date_letter}70', {
            "borders": {
                "right": {
                    "style": "SOLID_MEDIUM",
                    "color": {"red": 0, "green": 0, "blue": 0}
                }
            }
        })
        
        return hours_col, True
    
    def calculate_hours(self, start_time: str, end_time: str) -> float:
        """Calculate hours worked from start and end time."""
        start_hour, start_min = map(int, start_time.split(':'))
        end_hour, end_min = map(int, end_time.split(':'))
        
        start_dt = datetime(2000, 1, 1, start_hour, start_min)
        end_dt = datetime(2000, 1, 1, end_hour, end_min)
        
        # If end time is before start time, assume next day
        if end_dt <= start_dt:
            end_dt += timedelta(days=1)
        
        diff = end_dt - start_dt
        hours = diff.total_seconds() / 3600
        
        return round(hours, 2)
    
    def submit_hours(self, employee_name: str, date: str, hours: float) -> Dict[str, any]:
        """
        Submit hours worked for an employee on a specific date.
        
        Structure:
        - Find/create employee row (column B, starting from row 6)
        - Find/create date columns (HOURS + Date)
        - Write hours to the HOURS column for that date
        - Tip calculation happens automatically via formulas in date column
        
        Args:
            employee_name: Employee name
            date: Date in YYYY-MM-DD format
            hours: Hours worked
        
        Returns:
            Dictionary with submission details
        """
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        worksheet = self.get_or_create_month_sheet(date_obj)
        
        # Get or create date columns (returns hours column index)
        hours_col, col_created = self.get_or_create_date_column(date, worksheet)
        
        # Get or create employee row
        employee_row = self.get_or_create_employee_row(employee_name, worksheet)
        
        # Check if hours already submitted for this date
        existing_value = worksheet.cell(employee_row, hours_col).value
        if existing_value and str(existing_value).strip():
            raise Exception(f"Hours already submitted for {employee_name} on {date_obj.strftime('%d/%m/%Y')}. Manual manager approval required for duplicate entry.")
        
        # Write hours to the HOURS column for this date
        worksheet.update_cell(employee_row, hours_col, hours)
        
        return {
            "success": True,
            "row": employee_row,
            "employee_name": employee_name,
            "date": date_obj.strftime("%d/%m/%Y"),
            "hours": hours,
            "worksheet": worksheet.title,
            "date_column_created": col_created
        }
    
    def is_month_closed(self, date: str) -> bool:
        """Check if a month is closed for submissions."""
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        today = datetime.now()
        
        # Calculate the 2nd of the next month
        if date_obj.month == 12:
            cutoff_date = datetime(date_obj.year + 1, 1, 2)
        else:
            cutoff_date = datetime(date_obj.year, date_obj.month + 1, 2)
        
        return today > cutoff_date
    
    def submit_daily_tips(self, date: str, total_tips: float) -> Dict[str, any]:
        """
        Submit total daily tips (manager function).
        
        Writes total_tips to row 2 of the date's VALUES column (the column after HOURS).
        All formulas automatically recalculate.
        
        Args:
            date: Date in YYYY-MM-DD format
            total_tips: Total tips collected
        
        Returns:
            Dictionary with submission details
        """
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        worksheet = self.get_or_create_month_sheet(date_obj)
        
        # Get or create date columns (returns hours column index)
        hours_col, col_created = self.get_or_create_date_column(date, worksheet)
        
        # Date column is the next column after hours column
        date_col = hours_col + 1
        
        # Write total tips to row 2 of the DATE column (D2, F2, H2, etc.)
        worksheet.update_cell(2, date_col, total_tips)
        
        # Count employees (from column B)
        col_b = worksheet.col_values(2)
        employee_count = sum(1 for idx, name in enumerate(col_b, start=1) if idx > 5 and name.strip())
        
        return {
            "date": date_obj.strftime("%d/%m/%Y"),
            "total_tips": total_tips,
            "employee_count": employee_count,
            "formulas_injected": True
        }


# Global service instance
gs_service = GoogleSheetsService()
