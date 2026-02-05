"""
Setup verification script for Vila Acadia backend.
Run this script to verify your environment is configured correctly.
"""
import sys
import json
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_header(text):
    """Print formatted header."""
    print(f"\n{BOLD}{BLUE}{'=' * 60}{RESET}")
    print(f"{BOLD}{BLUE}{text.center(60)}{RESET}")
    print(f"{BOLD}{BLUE}{'=' * 60}{RESET}\n")


def print_success(text):
    """Print success message."""
    print(f"{GREEN}✓ {text}{RESET}")


def print_error(text):
    """Print error message."""
    print(f"{RED}✗ {text}{RESET}")


def print_warning(text):
    """Print warning message."""
    print(f"{YELLOW}⚠ {text}{RESET}")


def print_info(text):
    """Print info message."""
    print(f"{BLUE}ℹ {text}{RESET}")


def check_env_file():
    """Check if .env file exists and has required variables."""
    print_header("Checking Environment Configuration")
    
    env_path = Path(".env")
    if not env_path.exists():
        print_error(".env file not found")
        print_info("Create a .env file with the required variables")
        print_info("See README.md for details")
        return False
    
    print_success(".env file exists")
    
    # Read and parse .env file
    required_vars = ["GOOGLE_SHEET_ID", "SERVICE_ACCOUNT_JSON"]
    found_vars = {}
    
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        found_vars[key.strip()] = value.strip()
        
        all_present = True
        for var in required_vars:
            if var in found_vars and found_vars[var]:
                print_success(f"{var} is set")
                
                # Validate JSON format for SERVICE_ACCOUNT_JSON
                if var == "SERVICE_ACCOUNT_JSON":
                    try:
                        json.loads(found_vars[var])
                        print_success("  SERVICE_ACCOUNT_JSON is valid JSON")
                    except json.JSONDecodeError:
                        print_error("  SERVICE_ACCOUNT_JSON is not valid JSON")
                        all_present = False
            else:
                print_error(f"{var} is not set")
                all_present = False
        
        return all_present
    
    except Exception as e:
        print_error(f"Error reading .env file: {e}")
        return False


def check_dependencies():
    """Check if required Python packages are installed."""
    print_header("Checking Dependencies")
    
    required_packages = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("gspread", "gspread"),
        ("google.auth", "Google Auth"),
        ("dotenv", "python-dotenv"),
        ("pydantic", "Pydantic"),
    ]
    
    all_installed = True
    for module_name, display_name in required_packages:
        try:
            __import__(module_name)
            print_success(f"{display_name} is installed")
        except ImportError:
            print_error(f"{display_name} is NOT installed")
            all_installed = False
    
    if not all_installed:
        print_info("\nInstall missing packages with:")
        print_info("pip install -r requirements.txt")
    
    return all_installed


def test_google_sheets_connection():
    """Test connection to Google Sheets."""
    print_header("Testing Google Sheets Connection")
    
    try:
        from .config import settings
        from .gsheets_service import gs_service
        
        print_info("Attempting to connect to Google Sheets...")
        
        # Try to connect
        gs_service.connect()
        print_success("Connected to Google Sheets successfully")
        
        # Get spreadsheet info
        sheet = gs_service.get_spreadsheet()
        print_success(f"Spreadsheet title: {sheet.title}")
        print_success(f"Spreadsheet ID: {settings.google_sheet_id}")
        
        # Check for Settings sheet
        try:
            settings_worksheet = sheet.worksheet("Settings")
            print_success("'Settings' tab found")
            
            # Check headers
            headers = settings_worksheet.row_values(1)
            if "Name" in headers and "PIN" in headers:
                print_success("Settings sheet has correct headers")
            else:
                print_warning("Settings sheet may not have correct headers")
                print_info(f"  Found headers: {headers}")
            
            # Check for employees
            employees = gs_service.get_employee_settings()
            if employees:
                print_success(f"Found {len(employees)} employee(s) in Settings")
                for emp in employees:
                    print_info(f"  - {emp['name']} (PIN: {'*' * len(emp['pin'])})")
            else:
                print_warning("No employees found in Settings sheet")
        
        except Exception as e:
            print_error(f"Settings sheet error: {e}")
            return False
        
        return True
    
    except ImportError:
        print_error("Backend modules not found. Make sure you're in the project root.")
        return False
    except Exception as e:
        print_error(f"Connection failed: {e}")
        print_info("\nCommon issues:")
        print_info("1. Check GOOGLE_SHEET_ID is correct")
        print_info("2. Verify SERVICE_ACCOUNT_JSON is valid")
        print_info("3. Ensure sheet is shared with service account email")
        return False


def test_auth_logic():
    """Test authentication logic."""
    print_header("Testing Authentication Logic")
    
    try:
        from .gsheets_service import gs_service
        
        # Get employees
        employees = gs_service.get_employee_settings()
        
        if not employees:
            print_warning("No employees to test with")
            return True
        
        # Test with first employee
        test_employee = employees[0]
        name = test_employee['name']
        pin = test_employee['pin']
        
        print_info(f"Testing with: {name}")
        
        # Test valid credentials
        result = gs_service.verify_employee_pin(name, pin)
        if result:
            print_success("Valid credentials accepted")
        else:
            print_error("Valid credentials rejected!")
            return False
        
        # Test invalid PIN
        result = gs_service.verify_employee_pin(name, "0000")
        if not result:
            print_success("Invalid PIN rejected")
        else:
            print_error("Invalid PIN accepted!")
            return False
        
        # Test case insensitivity
        result = gs_service.verify_employee_pin(name.upper(), pin)
        if result:
            print_success("Case-insensitive matching works")
        else:
            print_error("Case-insensitive matching failed")
            return False
        
        return True
    
    except Exception as e:
        print_error(f"Authentication test failed: {e}")
        return False


def main():
    """Run all verification checks."""
    print_header("Vila Acadia Backend Setup Verification")
    print(f"{BOLD}This script will verify your backend configuration{RESET}\n")
    
    results = {
        "Environment Configuration": check_env_file(),
        "Dependencies": check_dependencies(),
    }
    
    # Only test Google Sheets if env and dependencies are OK
    if results["Environment Configuration"] and results["Dependencies"]:
        results["Google Sheets Connection"] = test_google_sheets_connection()
        if results["Google Sheets Connection"]:
            results["Authentication Logic"] = test_auth_logic()
    
    # Summary
    print_header("Verification Summary")
    
    all_passed = True
    for check, passed in results.items():
        if passed:
            print_success(f"{check}: PASSED")
        else:
            print_error(f"{check}: FAILED")
            all_passed = False
    
    print("\n" + "=" * 60 + "\n")
    
    if all_passed:
        print_success(f"{BOLD}All checks passed! ✨{RESET}")
        print_info("\nYou're ready to start the server:")
        print_info("  uvicorn src.backend.main:app --reload\n")
        print_info("Or visit http://localhost:8000/docs after starting\n")
        return 0
    else:
        print_error(f"{BOLD}Some checks failed ❌{RESET}")
        print_info("\nPlease fix the issues above and run this script again")
        print_info("See README.md and QUICKSTART.md for help\n")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Verification cancelled by user{RESET}")
        sys.exit(1)


