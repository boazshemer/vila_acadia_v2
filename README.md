# Vila Acadia - Employee Timesheet System

A modern timesheet management system using FastAPI and Google Sheets as a database.

## 📋 Project Overview

Vila Acadia is a web-based timesheet system that allows employees to:
- Clock in/out using a 4-digit PIN
- Track hours worked and tips collected
- Automatically calculate tip distribution based on hours worked

## 🏗️ Architecture

- **Backend:** FastAPI (Python)
- **Database:** Google Sheets (via gspread)
- **Frontend:** React + Vite + Tailwind CSS *(coming soon)*
- **Hosting:** Railway

## 🚀 Setup Instructions

### Prerequisites

1. **Python 3.11+** installed
2. **Google Cloud Service Account** with Google Sheets API enabled
3. **Google Sheet** set up with a "Settings" tab

### Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API
4. Create a Service Account:
   - Go to IAM & Admin → Service Accounts
   - Create a new service account
   - Generate a JSON key file
5. Share your Google Sheet with the service account email

### Google Sheet Structure

#### Settings Tab

Create a tab named "Settings" with the following structure:

| Name | PIN |
|------|-----|
| John Doe | 1234 |
| Jane Smith | 5678 |

#### Monthly Sheets

Monthly sheets (e.g., "January 2026") will be auto-created with these headers:
- Employee
- Date
- Clock In
- Clock Out
- Hours Worked
- Tips Collected
- Tip Rate (per hour)
- Payout

### Backend Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd vila_acadia
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Create a `.env` file in the project root:
   
   ```env
   # Google Sheets Configuration
   GOOGLE_SHEET_ID=your_google_sheet_id_here
   
   # Service Account JSON (paste as a single line)
   SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"...","private_key":"..."}
   
   # Server Configuration (optional)
   HOST=0.0.0.0
   PORT=8000
   ```
   
   **Note:** 
   - Get the `GOOGLE_SHEET_ID` from your sheet URL: `https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit`
   - Copy the entire JSON content from your service account key file and paste it as a single line

5. **Run the server**
   ```bash
   # Development mode with auto-reload
   uvicorn src.backend.main:app --reload --host 0.0.0.0 --port 8000
   
   # Or using the main module
   python -m src.backend.main
   ```

6. **Verify the setup**
   
   Open your browser and go to:
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## 📡 API Endpoints

### `GET /`
Root endpoint with API information.

### `GET /health`
Health check endpoint that verifies Google Sheets connectivity.

**Response:**
```json
{
  "status": "connected",
  "spreadsheet_id": "your_sheet_id",
  "spreadsheet_title": "Vila Acadia Timesheet",
  "message": "Successfully connected to Google Sheets"
}
```

### `POST /auth/verify`
Verify employee PIN authentication.

**Request:**
```json
{
  "name": "John Doe",
  "pin": "1234"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Authentication successful",
  "employee_name": "John Doe"
}
```

### `POST /submit-hours`
Submit hours worked by an employee.

**Request:**
```json
{
  "employee_name": "John Doe",
  "date": "2026-01-28",
  "start_time": "09:00",
  "end_time": "17:00"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Hours submitted successfully. New column created.",
  "hours_worked": 8.0,
  "date": "2026-01-28"
}
```

**Features:**
- Automatically calculates hours from start/end time
- Handles overnight shifts (e.g., 23:00 to 02:00)
- Creates date column if doesn't exist
- Validates month is still open (before 2nd of next month)
- Prevents overwriting existing data

### `POST /manager/submit-daily-tip`
Submit total daily tips and calculate payouts (Manager only).

**Request:**
```json
{
  "date": "2026-01-28",
  "total_tips": 500.00
}
```

**Response:**
```json
{
  "success": true,
  "message": "Daily tips submitted successfully. Formulas calculated for 5 employees.",
  "date": "2026-01-28",
  "total_tips": 500.00,
  "formulas_injected": true
}
```

**Features:**
- Writes total tips to Totals section
- Automatically injects formulas:
  - Total Hours (H) = SUM of all employee hours
  - Tip Rate (R) = T / H
- Validates month is still open
- Triggers automatic payout calculations

## 🔒 Security Features

### PIN Authentication
- Employees authenticate using a 4-digit PIN stored in the Settings tab
- Case-insensitive name matching
- Secure credential verification

### Race Condition Prevention
- **Check-then-Write** logic ensures no duplicate entries
- `check_entry_exists()` method validates before writing data
- Prevents overwriting existing data

### Manual Overwrite Protection
- System never overwrites cells containing data
- Always checks for existing entries before creating new ones

### Month Closure Protection
- Submissions blocked after the 2nd of the following month
- Prevents late entries that affect closed financial periods
- Validated on every submission

## 🏗️ Project Structure

```
vila_acadia/
├── src/
│   ├── backend/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration management
│   │   ├── gsheets_service.py   # Google Sheets integration
│   │   ├── models.py            # Pydantic models
│   │   ├── run.py               # Development server runner
│   │   └── verify_setup.py      # Setup verification script
│   └── frontend/                # React frontend (Vite + Tailwind)
├── tests/                       # Automated test suite
│   ├── conftest.py              # Pytest fixtures
│   ├── test_api_endpoints.py    # API tests
│   ├── test_gsheets_service.py  # Service tests
│   ├── test_models.py           # Model validation tests
│   ├── test_config.py           # Configuration tests
│   └── README.md                # Test documentation
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Pytest configuration
├── .env                         # Environment variables (not in git)
├── README.md                    # Main documentation
├── PROJECT_STATE.md             # Project status
├── QUICKSTART.md                # Quick setup guide
├── TECHNICAL_SPEC.md            # Technical specifications
├── DEPLOYMENT.md                # Deployment guide
├── TESTING.md                   # Testing guide
├── run_tests.py                 # Interactive test runner
└── verify.py                    # Setup verification wrapper
```

## 🧪 Testing

### Automated Test Suite

Run the comprehensive test suite with pytest:

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock httpx

# Run all tests
pytest

# Run with coverage report
pytest --cov=src/backend --cov-report=term

# Run specific test file
pytest tests/test_api_endpoints.py

# Interactive test runner
python run_tests.py
```

See `tests/README.md` for detailed testing documentation.

### Manual API Testing

#### Using the Interactive Docs

1. Go to http://localhost:8000/docs
2. Try the `/health` endpoint to verify connectivity
3. Try the `/auth/verify` endpoint with test credentials

#### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Verify authentication
curl -X POST http://localhost:8000/auth/verify \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "pin": "1234"}'
```

## 🚢 Deployment

### Option 1: Docker (Recommended)

```bash
# Build and run with Docker Compose
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

See `DOCKER.md` for complete Docker deployment guide.

### Option 2: Railway

1. Push to GitLab/GitHub
2. Connect Railway to your repository
3. Railway will auto-detect Dockerfile
4. Add environment variables in Railway dashboard:
   - `GOOGLE_SHEET_ID`
   - `SERVICE_ACCOUNT_JSON`
5. Deploy automatically

See `DEPLOYMENT.md` for detailed Railway instructions.

## 📚 Documentation

- `TECHNICAL_SPEC.md` - Technical specifications and formulas
- `PROJECT_STATE.md` - Current project state and progress
- `QUICKSTART.md` - Quick setup guide
- `DEPLOYMENT.md` - Railway deployment instructions
- `TESTING.md` - Testing guide and examples

## 🛠️ Development Guidelines

1. **Read documentation first** - Always check root documentation files before starting work
2. **Minimal diffs** - Make surgical changes, avoid rewriting entire files
3. **Zero redundancy** - No duplicate logic across backend/frontend
4. **Test thoroughly** - Verify Google Sheets integration and edge cases

## 🐛 Troubleshooting

### "Failed to connect to Google Sheets"
- Verify `GOOGLE_SHEET_ID` is correct
- Check that `SERVICE_ACCOUNT_JSON` is valid JSON
- Ensure the Google Sheet is shared with the service account email

### "Settings tab not found"
- Create a "Settings" tab in your Google Sheet
- Add headers: "Name" and "PIN"
- Add at least one employee entry

### "Authentication service temporarily unavailable"
- Check Google Sheets API quotas
- Verify service account has proper permissions
- Check application logs for detailed error messages

## 📝 Phase Status

### Phase 1 ✅ Complete
- [x] FastAPI backend foundation
- [x] Google Sheets integration
- [x] PIN authentication
- [x] Settings sheet management

### Phase 2 ✅ Complete
- [x] Dynamic date column creation
- [x] Hours submission with time calculation
- [x] Manager tip input
- [x] Automated formula injection (H, R formulas)
- [x] Month closure validation

### Phase 3 ⏳ Pending
- [ ] Build React frontend
- [ ] Employee dashboard
- [ ] Manager panel
- [ ] Visual payout reports

## 📄 License

[Specify your license here]

## 👥 Contributors

[List contributors here]

---

For technical details and implementation notes, see `TECHNICAL_SPEC.md`.

