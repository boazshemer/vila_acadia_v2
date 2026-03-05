"""
Google Sheets Service for Vila Acadia - Version 4
Implements tip distribution with dynamic Employee/Team Member split.
When 0 Team Members work: 100/0 split. When 1 Team Member works: 95/5 split. When 2+ Team Members work: 90/10 split.
Uses batch API calls to avoid Google Sheets rate limits.
"""
import gspread
import time
import logging
from google.oauth2.service_account import Credentials
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from .config import settings

logger = logging.getLogger(__name__)


class GoogleSheetsService:
    """Service for interacting with Google Sheets as a database."""

    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    # Sheet configuration
    SETTINGS_TAB = "Settings"

    # Tip split configuration (dynamic: 100/0 when 0 T members, 95/5 when 1 T member, 90/10 when 2+)
    EMPLOYEE_TIP_SHARE_ZERO_T = 1.0        # 100% for Employees (when 0 T work)
    TEAM_MEMBER_TIP_SHARE_ZERO_T = 0.0     # 0% for Team Members (when 0 T work)
    EMPLOYEE_TIP_SHARE_SINGLE_T = 0.95    # 95% for Employees (when 1 T works)
    TEAM_MEMBER_TIP_SHARE_SINGLE_T = 0.05  # 5% for Team Members (when 1 T works)
    EMPLOYEE_TIP_SHARE_MULTI_T = 0.9      # 90% for Employees (when 2+ T work)
    TEAM_MEMBER_TIP_SHARE_MULTI_T = 0.1   # 10% for Team Members (when 2+ T work)

    # Sheet layout constants
    HEADER_ROW = 9        # Row for column headers (שם העובד, סוג, HOURS, date)
    DATA_START_ROW = 10   # First row of employee data
    DATA_END_ROW = 79     # Last row of employee data (70 employees max)
    TYPE_COL = 3          # Column C for employee type (E/T)
    DATE_COLS_START = 4   # Date columns start at column D
    TOTAL_MONTHLY_HEADER = "TOTAL MONTHLY TIPS"

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

    def _retry_api_call(self, func, *args, **kwargs):
        """Retry an API call with exponential backoff on rate limit errors (429)."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except gspread.exceptions.APIError as e:
                if e.response.status_code == 429 and attempt < max_retries - 1:
                    wait = (attempt + 1) * 10  # 10s, 20s, 30s
                    logger.warning(f"Rate limited (429), retrying in {wait}s (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait)
                else:
                    raise

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
        """Fetch employee roster, PINs, and types from the Settings tab."""
        try:
            sheet = self.get_spreadsheet()
            settings_worksheet = sheet.worksheet(self.SETTINGS_TAB)
            records = settings_worksheet.get_all_records()

            logger.info(f"Read {len(records)} records from Settings sheet")

            employees = []
            for idx, record in enumerate(records):
                name = (record.get("Name") or record.get("name") or
                       record.get("Employee Name") or record.get("employee name") or "").strip()
                pin = str(record.get("PIN") or record.get("pin") or
                         record.get("Pin") or "").strip()
                emp_type = str(record.get("Type") or record.get("type") or
                              record.get("סוג") or "E").strip().upper()

                # Validate type - default to E if invalid
                if emp_type not in ("E", "T"):
                    emp_type = "E"

                if name and pin:
                    employees.append({"name": name, "pin": pin, "type": emp_type})
                    logger.info(f"Added employee: name='{name}', type='{emp_type}'")
                else:
                    logger.warning(f"Skipped record {idx} - name: '{name}', pin: '{pin}'")

            logger.info(f"Total employees found: {len(employees)}")
            return employees

        except gspread.WorksheetNotFound:
            raise Exception(f"'{self.SETTINGS_TAB}' tab not found in the spreadsheet")
        except Exception as e:
            raise Exception(f"Error reading employee settings: {str(e)}")

    def verify_employee_pin(self, name: str, pin: str) -> Tuple[bool, str, str]:
        """
        Verify an employee's PIN against the Settings sheet.

        Returns:
            Tuple of (is_valid, employee_type, canonical_name).
            canonical_name is the exact name as stored in the Settings sheet.
        """
        try:
            employees = self.get_employee_settings()
            logger.info(f"Verifying PIN for '{name}', found {len(employees)} employees")

            for employee in employees:
                if employee["name"].lower() == name.lower() and employee["pin"] == pin:
                    return True, employee.get("type", "E"), employee["name"]

            logger.warning(f"No match found for employee '{name}'")
            return False, "", ""

        except Exception as e:
            logger.error(f"Error verifying employee PIN: {e}", exc_info=True)
            raise

    def get_or_create_month_sheet(self, date: Optional[datetime] = None) -> gspread.Worksheet:
        """Get or create a worksheet for the month."""
        if date is None:
            date = datetime.now()

        sheet_name = date.strftime("%m-%Y")
        sheet = self.get_spreadsheet()

        try:
            worksheet = sheet.worksheet(sheet_name)

            # Check if dashboard is initialized (A10 should have "1")
            a10_value = worksheet.cell(self.DATA_START_ROW, 1).value
            if not a10_value or a10_value != "1":
                self._initialize_dashboard(worksheet)

            return worksheet

        except gspread.WorksheetNotFound:
            worksheet = sheet.add_worksheet(
                title=sheet_name,
                rows=100,
                cols=50
            )
            self._initialize_dashboard(worksheet)
            return worksheet

    def _initialize_dashboard(self, worksheet: gspread.Worksheet) -> None:
        """Initialize the headers and structure for a monthly worksheet."""
        # Add employee numbers in Column A (rows 10-79)
        a10_value = worksheet.cell(self.DATA_START_ROW, 1).value
        if not a10_value or a10_value != "1":
            employee_numbers = [[i] for i in range(1, 71)]
            self._retry_api_call(
                worksheet.update,
                f'A{self.DATA_START_ROW}:A{self.DATA_END_ROW}',
                employee_numbers,
                value_input_option='USER_ENTERED'
            )

        # Add headers in row 9 — batch both cells together
        b9_value = worksheet.cell(self.HEADER_ROW, 2).value
        if not b9_value or b9_value != 'שם העובד':
            self._retry_api_call(
                worksheet.batch_update,
                [
                    {'range': f'B{self.HEADER_ROW}', 'values': [['שם העובד']]},
                    {'range': f'C{self.HEADER_ROW}', 'values': [['סוג']]},
                ],
                value_input_option='USER_ENTERED'
            )

            self._retry_api_call(
                worksheet.format,
                f'A{self.HEADER_ROW}:C{self.HEADER_ROW}', {
                    "textFormat": {"bold": True},
                    "backgroundColor": {"red": 0.85, "green": 0.92, "blue": 0.83},
                    "horizontalAlignment": "CENTER"
                }
            )

        # Freeze header row and first 3 columns (A=number, B=name, C=type)
        worksheet.freeze(rows=self.HEADER_ROW, cols=3)

    def _col_index_to_letter(self, col_index: int) -> str:
        """Convert column index (1-based) to letter (A, B, C, ...)."""
        result = ""
        while col_index > 0:
            col_index -= 1
            result = chr(col_index % 26 + ord('A')) + result
            col_index //= 26
        return result

    def get_or_create_employee_row(self, employee_name: str, worksheet: gspread.Worksheet, employee_type: str = "E") -> int:
        """
        Get or create row for a specific employee.
        Employees start from row 10. Names in column B, types in column C.
        """
        col_b = worksheet.col_values(2)  # Column B

        # Search for employee (case-insensitive, skip header rows 1-9)
        for idx, name in enumerate(col_b, start=1):
            if idx >= self.DATA_START_ROW and name.strip().lower() == employee_name.lower().strip():
                return idx

        # Employee not found, add to next row
        next_row = len(col_b) + 1
        if next_row < self.DATA_START_ROW:
            next_row = self.DATA_START_ROW
        if next_row > self.DATA_END_ROW:
            raise ValueError("Maximum number of employees (70) reached")

        # Batch: write name + type in one call
        self._retry_api_call(
            worksheet.batch_update,
            [
                {'range': f'B{next_row}', 'values': [[employee_name]]},
                {'range': f'C{next_row}', 'values': [[employee_type]]},
            ],
            value_input_option='USER_ENTERED'
        )
        return next_row

    def get_or_create_date_column(self, date: str, worksheet: gspread.Worksheet) -> Tuple[int, bool]:
        """
        Get or create columns for a specific date with Employee/Team Member split.

        Each date gets 2 columns:
        - Hours column: labels (rows 2-8), "HOURS" header (row 9), hours data (rows 10-79)
        - Date column: formulas (rows 2-8), date (row 9), tip formulas (rows 10-79)
        """
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        date_formatted = date_obj.strftime("%d/%m/%Y")

        # Get header row (row 9) to search for existing date
        row9 = worksheet.row_values(self.HEADER_ROW)

        # Search for existing date column
        for idx, header in enumerate(row9, start=1):
            if idx >= self.DATE_COLS_START and header == date_formatted:
                return idx - 1, False

        # Date not found, create new columns
        # Check if TOTAL MONTHLY TIPS column exists - new date goes at its position
        total_monthly_col = None
        for idx, header in enumerate(row9, start=1):
            if header == self.TOTAL_MONTHLY_HEADER:
                total_monthly_col = idx
                break

        if total_monthly_col is not None:
            next_col = total_monthly_col
        else:
            next_col = len(row9) + 1
            if next_col < self.DATE_COLS_START:
                next_col = self.DATE_COLS_START

        hours_col = next_col
        date_col = next_col + 1

        hl = self._col_index_to_letter(hours_col)   # hours letter
        dl = self._col_index_to_letter(date_col)     # date letter
        dr = self.DATA_START_ROW  # 10
        er = self.DATA_END_ROW    # 79

        # === BUILD ALL DATA IN ONE BATCH ===
        labels = [
            ['TOTAL TIP'],
            ['TOTAL TIP E'],
            ['TOTAL TIP T'],
            ['TOTAL HOUR E'],
            ['TOTAL HOUR T'],
            ['TIP PER HOUR E'],
            ['TIP PER HOUR T'],
        ]

        empty_cells = [[''] for _ in range(dr, er + 1)]

        # Count T-type employees with hours > 0 for this date
        t_count = f'COUNTIFS($C${dr}:$C${er},"T",{hl}{dr}:{hl}{er},">0")'

        formulas_batch = [
            # Row 3: TOTAL TIP E — 100% if 0 T work, 95% if 1 T works, 90% if 2+ T work
            [f'=IF({t_count}=0,{dl}2*{self.EMPLOYEE_TIP_SHARE_ZERO_T},IF({t_count}=1,{dl}2*{self.EMPLOYEE_TIP_SHARE_SINGLE_T},{dl}2*{self.EMPLOYEE_TIP_SHARE_MULTI_T}))'],
            # Row 4: TOTAL TIP T — 0% if 0 T work, 5% if 1 T works, 10% if 2+ T work
            [f'=IF({t_count}=0,{dl}2*{self.TEAM_MEMBER_TIP_SHARE_ZERO_T},IF({t_count}=1,{dl}2*{self.TEAM_MEMBER_TIP_SHARE_SINGLE_T},{dl}2*{self.TEAM_MEMBER_TIP_SHARE_MULTI_T}))'],
            [f'=SUMPRODUCT(($C${dr}:$C${er}="E")*({hl}{dr}:{hl}{er}))'],
            [f'=SUMPRODUCT(($C${dr}:$C${er}="T")*({hl}{dr}:{hl}{er}))'],
            [f'=IF({dl}5>0,{dl}3/{dl}5,0)'],
            [f'=IF({dl}6>0,{dl}4/{dl}6,0)'],
        ]

        tip_formulas = []
        for row in range(dr, er + 1):
            tip_formulas.append([
                f'=IF($C{row}="E",{hl}{row}*${dl}$7,IF($C{row}="T",{hl}{row}*${dl}$8,0))'
            ])

        # ONE batch_update call for ALL data (was 6 separate calls)
        self._retry_api_call(
            worksheet.batch_update,
            [
                {'range': f'{hl}2:{hl}8', 'values': labels},
                {'range': f'{hl}{self.HEADER_ROW}', 'values': [['HOURS']]},
                {'range': f'{hl}{dr}:{hl}{er}', 'values': empty_cells},
                {'range': f'{dl}3:{dl}8', 'values': formulas_batch},
                {'range': f'{dl}{self.HEADER_ROW}', 'values': [[date_formatted]]},
                {'range': f'{dl}{dr}:{dl}{er}', 'values': tip_formulas},
            ],
            value_input_option='USER_ENTERED'
        )

        # ONE batch_format call for ALL formatting (was 9 separate calls)
        self._retry_api_call(
            worksheet.batch_format,
            [
                # Dashboard labels (hours col rows 2-8) - bold, light green
                {"range": f'{hl}2:{hl}8', "format": {
                    "textFormat": {"bold": True},
                    "backgroundColor": {"red": 0.85, "green": 0.92, "blue": 0.83},
                    "horizontalAlignment": "CENTER"
                }},
                # Header row (row 9) - bold, light green
                {"range": f'{hl}{self.HEADER_ROW}:{dl}{self.HEADER_ROW}', "format": {
                    "textFormat": {"bold": True},
                    "backgroundColor": {"red": 0.85, "green": 0.92, "blue": 0.83},
                    "horizontalAlignment": "CENTER"
                }},
                # Date column row 2 (TOTAL TIP - light orange for manager input)
                {"range": f'{dl}2', "format": {
                    "textFormat": {"bold": True},
                    "backgroundColor": {"red": 1.0, "green": 0.85, "blue": 0.7},
                    "horizontalAlignment": "CENTER",
                    "numberFormat": {"type": "CURRENCY", "pattern": "#,##0 \u20AA"}
                }},
                # TOTAL TIP E and T values (rows 3-4) - currency
                {"range": f'{dl}3:{dl}4', "format": {
                    "textFormat": {"bold": True},
                    "backgroundColor": {"red": 0.85, "green": 0.92, "blue": 0.83},
                    "horizontalAlignment": "CENTER",
                    "numberFormat": {"type": "CURRENCY", "pattern": "#,##0 \u20AA"}
                }},
                # TOTAL HOUR E and T values (rows 5-6) - number
                {"range": f'{dl}5:{dl}6', "format": {
                    "textFormat": {"bold": True},
                    "backgroundColor": {"red": 0.85, "green": 0.92, "blue": 0.83},
                    "horizontalAlignment": "CENTER",
                    "numberFormat": {"type": "NUMBER", "pattern": "0.00"}
                }},
                # TIP PER HOUR E and T values (rows 7-8) - currency
                {"range": f'{dl}7:{dl}8', "format": {
                    "textFormat": {"bold": True},
                    "backgroundColor": {"red": 0.85, "green": 0.92, "blue": 0.83},
                    "horizontalAlignment": "CENTER",
                    "numberFormat": {"type": "CURRENCY", "pattern": "#,##0 \u20AA"}
                }},
                # Hours data column (light yellow + 2 decimals)
                {"range": f'{hl}{dr}:{hl}{er}', "format": {
                    "backgroundColor": {"red": 1.0, "green": 0.95, "blue": 0.8},
                    "numberFormat": {"type": "NUMBER", "pattern": "0.00"}
                }},
                # Tips column (currency with shekel)
                {"range": f'{dl}{dr}:{dl}{er}', "format": {
                    "numberFormat": {"type": "CURRENCY", "pattern": "#,##0 \u20AA"}
                }},
                # Right border on date column for visual separation
                {"range": f'{dl}1:{dl}{er}', "format": {
                    "borders": {
                        "right": {
                            "style": "SOLID_MEDIUM",
                            "color": {"red": 0, "green": 0, "blue": 0}
                        }
                    }
                }},
            ]
        )

        # Update or create the TOTAL MONTHLY TIPS column
        self._update_total_monthly_column(worksheet)

        return hours_col, True

    def _update_total_monthly_column(self, worksheet: gspread.Worksheet) -> None:
        """
        Create or update the TOTAL MONTHLY TIPS summary column.
        Always placed as the rightmost column, summing all tip values per employee.
        """
        row9 = worksheet.row_values(self.HEADER_ROW)
        if not row9:
            return

        # Collect all DATE columns (they contain dates like dd/mm/yyyy, not "HOURS" or TOTAL)
        date_col_indices = []
        for idx, header in enumerate(row9, start=1):
            if idx >= self.DATE_COLS_START:
                if header and header != "HOURS" and header != self.TOTAL_MONTHLY_HEADER:
                    date_col_indices.append(idx)

        if not date_col_indices:
            return  # No date columns exist yet

        last_date_col = date_col_indices[-1]
        total_col = last_date_col + 1
        tl = self._col_index_to_letter(total_col)
        dr = self.DATA_START_ROW   # 10
        er = self.DATA_END_ROW     # 79

        # Get column letters for all DATE columns (E, G, I, ...)
        date_col_letters = [self._col_index_to_letter(c) for c in date_col_indices]

        # Build formulas — rows 3-4 SUM daily values (each day has its own dynamic split)
        sum_row2 = '+'.join(f'{dc}2' for dc in date_col_letters)
        sum_row3 = '+'.join(f'{dc}3' for dc in date_col_letters)
        sum_row4 = '+'.join(f'{dc}4' for dc in date_col_letters)
        sum_row5 = '+'.join(f'{dc}5' for dc in date_col_letters)
        sum_row6 = '+'.join(f'{dc}6' for dc in date_col_letters)

        dashboard_formulas = [
            [f'={sum_row2}'],
            [f'={sum_row3}'],
            [f'={sum_row4}'],
            [f'={sum_row5}'],
            [f'={sum_row6}'],
            [''],
            [''],
        ]

        tip_sum_formulas = []
        for row in range(dr, er + 1):
            sum_refs = '+'.join(f'{dc}{row}' for dc in date_col_letters)
            tip_sum_formulas.append([f'={sum_refs}'])

        # ONE batch_update for ALL data (was 3 separate calls)
        self._retry_api_call(
            worksheet.batch_update,
            [
                {'range': f'{tl}{self.HEADER_ROW}', 'values': [[self.TOTAL_MONTHLY_HEADER]]},
                {'range': f'{tl}2:{tl}8', 'values': dashboard_formulas},
                {'range': f'{tl}{dr}:{tl}{er}', 'values': tip_sum_formulas},
            ],
            value_input_option='USER_ENTERED'
        )

        # ONE batch_format for ALL formatting (was 8 separate calls)
        self._retry_api_call(
            worksheet.batch_format,
            [
                # Header row 9 - bold, light blue
                {"range": f'{tl}{self.HEADER_ROW}', "format": {
                    "textFormat": {"bold": True},
                    "backgroundColor": {"red": 0.68, "green": 0.85, "blue": 0.95},
                    "horizontalAlignment": "CENTER"
                }},
                # Dashboard rows 2-8 - bold, light blue
                {"range": f'{tl}2:{tl}8', "format": {
                    "textFormat": {"bold": True},
                    "backgroundColor": {"red": 0.68, "green": 0.85, "blue": 0.95},
                    "horizontalAlignment": "CENTER"
                }},
                # Row 2 - currency
                {"range": f'{tl}2', "format": {
                    "numberFormat": {"type": "CURRENCY", "pattern": "#,##0 \u20AA"}
                }},
                # Rows 3-4 - currency
                {"range": f'{tl}3:{tl}4', "format": {
                    "numberFormat": {"type": "CURRENCY", "pattern": "#,##0 \u20AA"}
                }},
                # Rows 5-6 - number
                {"range": f'{tl}5:{tl}6', "format": {
                    "numberFormat": {"type": "NUMBER", "pattern": "0.00"}
                }},
                # Rows 7-8 - currency
                {"range": f'{tl}7:{tl}8', "format": {
                    "numberFormat": {"type": "CURRENCY", "pattern": "#,##0 \u20AA"}
                }},
                # Employee data - currency, light blue background
                {"range": f'{tl}{dr}:{tl}{er}', "format": {
                    "backgroundColor": {"red": 0.85, "green": 0.92, "blue": 0.97},
                    "numberFormat": {"type": "CURRENCY", "pattern": "#,##0 \u20AA"},
                    "textFormat": {"bold": True}
                }},
                # Left border for visual separation
                {"range": f'{tl}1:{tl}{er}', "format": {
                    "borders": {
                        "left": {
                            "style": "SOLID_MEDIUM",
                            "color": {"red": 0, "green": 0, "blue": 0}
                        }
                    }
                }},
            ]
        )

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

    def submit_hours(self, employee_name: str, date: str, hours: float, employee_type: str = "E") -> Dict[str, any]:
        """Submit hours worked for an employee on a specific date."""
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        worksheet = self.get_or_create_month_sheet(date_obj)

        hours_col, col_created = self.get_or_create_date_column(date, worksheet)
        employee_row = self.get_or_create_employee_row(employee_name, worksheet, employee_type)

        # Check if hours already submitted for this date
        existing_value = worksheet.cell(employee_row, hours_col).value
        if existing_value and str(existing_value).strip():
            raise Exception(f"Hours already submitted for {employee_name} on {date_obj.strftime('%d/%m/%Y')}. Manual manager approval required for duplicate entry.")

        self._retry_api_call(worksheet.update_cell, employee_row, hours_col, hours)

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

        if date_obj.month == 12:
            cutoff_date = datetime(date_obj.year + 1, 1, 2)
        else:
            cutoff_date = datetime(date_obj.year, date_obj.month + 1, 2)

        return today > cutoff_date

    def submit_daily_tips(self, date: str, total_tips: float) -> Dict[str, any]:
        """
        Submit total daily tips (manager function).
        Writes total_tips to row 2 of the date's values column.
        All formulas automatically recalculate the dynamic tip split
        (95/5 when 1 T member works, 90/10 when 2+ T members work).
        """
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        worksheet = self.get_or_create_month_sheet(date_obj)

        hours_col, col_created = self.get_or_create_date_column(date, worksheet)
        date_col = hours_col + 1

        # Write total tips to row 2 of the DATE column
        self._retry_api_call(worksheet.update_cell, 2, date_col, total_tips)

        # Count employees (from column B, starting from DATA_START_ROW)
        col_b = worksheet.col_values(2)
        employee_count = sum(
            1 for idx, name in enumerate(col_b, start=1)
            if idx >= self.DATA_START_ROW and name.strip()
        )

        return {
            "date": date_obj.strftime("%d/%m/%Y"),
            "total_tips": total_tips,
            "employee_count": employee_count,
            "formulas_injected": True
        }


# Global service instance
gs_service = GoogleSheetsService()
