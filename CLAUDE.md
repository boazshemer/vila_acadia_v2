# Vila Acadia - Project Guide for Claude

## What Is This Project?
Employee timesheet & tip distribution system for Vila Acadia restaurant.
Employees submit work hours via a web app, managers enter daily tips, and the system auto-calculates tip payouts per employee in Google Sheets.

## Tech Stack
- **Backend:** FastAPI (Python 3.11+), Google Sheets via `gspread`
- **Frontend:** React 18 + Vite + Tailwind CSS + Framer Motion
- **Database:** Google Sheets (no traditional DB)
- **Deployment:** Docker / Railway
- **Hosting:** Railway (frontend + backend served together)

## Project Structure
```
vila_acadia/
├── src/
│   ├── backend/
│   │   ├── main.py              # FastAPI app, all endpoints
│   │   ├── gsheets_service.py   # Core logic: Google Sheets read/write/formulas
│   │   ├── models.py            # Pydantic request/response models
│   │   ├── config.py            # Environment variables (Pydantic Settings)
│   │   └── run.py               # Dev server runner
│   └── frontend/
│       └── src/
│           ├── App.jsx           # Router: 4 routes
│           ├── pages/
│           │   ├── EmployeeLogin.jsx      # Name + PIN login
│           │   ├── EmployeeTimeEntry.jsx  # Date + start/end time form
│           │   ├── ManagerLogin.jsx       # Password login
│           │   └── ManagerDashboard.jsx   # Daily tip input + employee list
│           ├── services/api.js   # Axios client (30s timeout)
│           ├── components/       # LoadingSpinner
│           └── utils/            # timeCalculator (hours calc, date utils)
├── Dockerfile                    # Multi-stage: frontend build → Python → runtime
├── docker-compose.yml
├── requirements.txt
└── env.example
```

## API Endpoints
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Health check, verifies Google Sheets connection |
| POST | `/auth/verify` | Employee PIN authentication |
| POST | `/manager/auth` | Manager password authentication |
| POST | `/submit-hours` | Employee submits hours for a date |
| POST | `/manager/submit-daily-tip` | Manager submits total daily tips |

## Google Sheets Structure

### Tabs
- **Settings** — Employee roster: Name, PIN, Type (E=Employee, T=Team Member)
- **MM-YYYY** (e.g., "02-2026") — Monthly worksheet, created automatically

### Monthly Worksheet Layout
```
Row 1:  Empty
Row 2:  TOTAL TIP          | [manager input per day]  | TOTAL MONTHLY TIPS
Row 3:  TOTAL TIP E        | =val*0.9                 | =sum*0.9
Row 4:  TOTAL TIP T        | =val*0.1                 | =sum*0.1
Row 5:  TOTAL HOUR E       | =SUMPRODUCT(E hours)     | sum of all days
Row 6:  TOTAL HOUR T       | =SUMPRODUCT(T hours)     | sum of all days
Row 7:  TIP PER HOUR E     | =IF(h>0,tips/h,0)        | (empty)
Row 8:  TIP PER HOUR T     | =IF(h>0,tips/h,0)        | (empty)
Row 9:  שם העובד | סוג | HOURS | dd/mm/yyyy | HOURS | dd/mm/yyyy | ... | TOTAL MONTHLY TIPS
Row 10-79: Employee data rows
```

Each date creates a PAIR of columns:
- **HOURS column** — Text labels (rows 2-8), "HOURS" header (row 9), hours data (rows 10-79)
- **DATE column** — Formulas (rows 2-8), date header (row 9), tip formulas (rows 10-79)

**TOTAL MONTHLY TIPS** — Always the rightmost column, uses explicit references (=E10+G10+I10...) to sum only DATE columns per employee.

### Tip Distribution Formula
- 90% of daily tips → split among E (Employee) type by hours
- 10% of daily tips → split among T (Team Member) type by hours
- Per-employee payout = their_hours × (type_share / type_total_hours)

## Key Implementation Details

### gsheets_service.py — The Core File
- `GoogleSheetsService` class with constants: `HEADER_ROW=9`, `DATA_START_ROW=10`, `DATA_END_ROW=79`, `DATE_COLS_START=4`
- `get_or_create_month_sheet()` — Creates/gets monthly tab, initializes dashboard
- `get_or_create_date_column()` — Creates HOURS+DATE column pair, detects TOTAL MONTHLY TIPS column and overwrites it (recreated after)
- `_update_total_monthly_column()` — Creates/updates the TOTAL MONTHLY TIPS column at rightmost position. Uses explicit column refs (`=E2+G2`) not SUMPRODUCT (SUMPRODUCT fails with text in HOURS columns)
- `submit_hours()` — Writes hours to correct cell, prevents duplicates
- `submit_daily_tips()` — Writes total tip amount to row 2 of DATE column

### Frontend Auth Flow
- Employee: name + 4-digit PIN → verified against Settings tab → stored in localStorage
- Manager: password → verified against `MANAGER_PASSWORD` env var → token in localStorage

### API Timeout
Set to **30 seconds** in `api.js` because Google Sheets API calls (especially when creating new date columns + TOTAL column) can take 15-20 seconds.

## Configuration (Environment Variables)
| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `GOOGLE_SHEET_ID` | Yes | — | Google Sheet ID |
| `SERVICE_ACCOUNT_JSON` | Yes | — | Google service account credentials JSON |
| `MANAGER_PASSWORD` | No | "manager2024" | Manager login password |
| `FRONTEND_URL` | No | "http://localhost:3000" | CORS origin |
| `ALLOWED_ORIGINS` | No | "" | Additional CORS origins (comma-separated) |
| `HOST` | No | "0.0.0.0" | Server bind address |
| `PORT` | No | 8000 | Server port |

## Dev Setup
```bash
# Backend
pip install -r requirements.txt
cp env.example .env  # Fill in GOOGLE_SHEET_ID and SERVICE_ACCOUNT_JSON
python -m uvicorn src.backend.main:app --reload --port 8000

# Frontend (separate terminal)
cd src/frontend
npm install
npm run dev  # Starts on port 3000, proxies /api to :8000
```

## Changes Log — February 2026

### Session: Feb 11, 2026
1. **Removed demo password hint** from ManagerLogin.jsx — was exposing "manager2024" to anyone
2. **Added TOTAL MONTHLY TIPS column** to Google Sheets monthly worksheets:
   - Always rightmost column, auto-shifts when new days added
   - Sums tip payouts per employee across all days
   - Dashboard rows show monthly totals (rows 2-6), rows 7-8 left empty
   - Light blue formatting to distinguish from daily columns
   - Initially used SUMPRODUCT formula (failed due to text in HOURS cols), fixed to explicit column refs
3. **Removed employee name autocomplete** from EmployeeLogin.jsx — removed hardcoded name list and datalist dropdown
4. **Increased API timeout** from 10s to 30s — TOTAL MONTHLY TIPS adds ~10 extra Google Sheets API calls per new date column

### Known Issues / Future Improvements
- Manager auth uses plain text password comparison (should hash)
- JWT tokens are placeholder (need proper implementation with expiration)
- No rate limiting on auth endpoints
- `managerAPI.getEmployees()` returns empty array (TODO — needs backend endpoint)
- Consider batching Google Sheets API calls to reduce latency
- No audit logging for who submitted/changed what
