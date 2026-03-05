# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What Is This Project?
Employee timesheet & tip distribution system for Vila Acadia restaurant.
Employees submit work hours via a web app, managers enter daily tips, and the system auto-calculates tip payouts per employee in Google Sheets.

## Tech Stack
- **Backend:** FastAPI (Python 3.11+), Google Sheets via `gspread`
- **Frontend:** React 18 + Vite + Tailwind CSS + Framer Motion
- **Database:** Google Sheets (no traditional DB)
- **Deployment:** Railway (auto-deploys from `main` branch on push)

## Dev Commands

```bash
# Backend
pip install -r requirements.txt
cp env.example .env  # Fill in GOOGLE_SHEET_ID and SERVICE_ACCOUNT_JSON
python -m uvicorn src.backend.main:app --reload --port 8000

# Frontend (separate terminal)
cd src/frontend
npm install
npm run dev  # Starts on port 3000, proxies /api to :8000

# Docker (full stack)
docker-compose up --build
```

No test suite is currently configured (pytest is in requirements.txt but no test files exist).

## Architecture

### Request Flow
Frontend (React) → FastAPI endpoints → `gsheets_service.py` → Google Sheets API (`gspread`)

### Key Files
- **`src/backend/gsheets_service.py`** — Core file. All Google Sheets read/write/formula logic. This is where most bugs and changes happen.
- **`src/backend/main.py`** — FastAPI app with 5 endpoints. Serves built frontend as static files in production.
- **`src/backend/config.py`** — Pydantic Settings for env vars.
- **`src/frontend/src/pages/ManagerDashboard.jsx`** — Daily tip input form (single centered card).
- **`src/frontend/src/pages/EmployeeTimeEntry.jsx`** — Date + start/end time form.
- **`src/frontend/src/services/api.js`** — Axios client with 30s timeout (Google Sheets calls can take 15-20s).

### API Endpoints
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Health check, verifies Google Sheets connection |
| POST | `/auth/verify` | Employee PIN auth (case-insensitive, returns canonical name) |
| POST | `/manager/auth` | Manager password auth |
| POST | `/submit-hours` | Employee submits hours for a date |
| POST | `/manager/submit-daily-tip` | Manager submits total daily tips |

## Google Sheets Structure

### Tabs
- **Settings** — Employee roster: columns `Employee Name`, `Type` (E=Employee, T=Team Member), `PIN`
- **MM-YYYY** (e.g., "02-2026") — Monthly worksheet, created automatically

### Monthly Worksheet Layout
```
Row 1:  Empty
Row 2:  TOTAL TIP          | [manager input per day]  | TOTAL MONTHLY TIPS
Row 3:  TOTAL TIP E        | =IF(COUNTIFS(...)<=1,val*0.95,val*0.9) | =sum of daily row 3
Row 4:  TOTAL TIP T        | =IF(COUNTIFS(...)<=1,val*0.05,val*0.1) | =sum of daily row 4
Row 5:  TOTAL HOUR E       | =SUMPRODUCT(E hours)     | sum of all days
Row 6:  TOTAL HOUR T       | =SUMPRODUCT(T hours)     | sum of all days
Row 7:  TIP PER HOUR E     | =IF(h>0,tips/h,0)        | (empty)
Row 8:  TIP PER HOUR T     | =IF(h>0,tips/h,0)        | (empty)
Row 9:  שם העובד | סוג | HOURS | dd/mm/yyyy | HOURS | dd/mm/yyyy | ... | TOTAL MONTHLY TIPS
Row 10-79: Employee data rows
```

Each date creates a **PAIR** of columns: HOURS (data) + DATE (formulas).
**TOTAL MONTHLY TIPS** is always the rightmost column, uses explicit refs (`=E10+G10+I10...`) not SUMPRODUCT (SUMPRODUCT fails with text in HOURS columns).

### Tip Distribution (Dynamic Split)
The split depends on how many Team Members (T) have hours > 0 for that day:
- **0 T members working:** 100% → E (Employees), 0% → T (Team Members)
- **1 T member working:** 95% → E (Employees), 5% → T (Team Members)
- **2+ T members working:** 90% → E (Employees), 10% → T (Team Members)

The split is implemented as nested Google Sheets `IF`/`COUNTIFS` formulas in each daily column (rows 3-4), so it recalculates automatically when employees submit or change hours.

## Critical Implementation Details

### Google Sheets API Rate Limits
Google allows 60 write requests/minute per user. The code uses **batch operations** to stay within limits:
- `batch_update()` — groups multiple cell writes into 1 API call
- `batch_format()` — groups multiple format changes into 1 API call
- `_retry_api_call()` — auto-retries with exponential backoff on 429 errors

**Creating a new date column uses ~5-6 API calls** (was ~28 before batching).

### gspread batch_format Syntax
`batch_format` expects a list of **dicts**, NOT tuples:
```python
# CORRECT
worksheet.batch_format([
    {"range": "A1:B2", "format": {"textFormat": {"bold": True}}}
])

# WRONG — causes "tuple indices must be integers or slices, not str"
worksheet.batch_format([
    ("A1:B2", {"textFormat": {"bold": True}})
])
```

### Sheet Layout Constants
In `GoogleSheetsService`: `HEADER_ROW=9`, `DATA_START_ROW=10`, `DATA_END_ROW=79`, `DATE_COLS_START=4`

### Auth Flow
- Employee login is **case-insensitive** — name is matched lowercase but the canonical name from Settings is returned and used for sheet writes.
- `verify_employee_pin()` returns `Tuple[bool, str, str]` → `(is_valid, employee_type, canonical_name)`.
- Manager auth uses plain text password comparison against `MANAGER_PASSWORD` env var.

### Error Handling Gotcha
Never silently catch exceptions in `gsheets_service.py` — a previous bug silently returned `False` on Google Sheets connection errors, making all logins fail with "Invalid credentials" instead of surfacing the real error. Always log and re-raise.

## Configuration (Environment Variables)
| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `GOOGLE_SHEET_ID` | Yes | — | Google Sheet ID |
| `SERVICE_ACCOUNT_JSON` | Yes | — | Service account credentials JSON |
| `MANAGER_PASSWORD` | No | "manager2024" | Manager login password |
| `FRONTEND_URL` | No | "http://localhost:3000" | CORS origin |
| `ALLOWED_ORIGINS` | No | "" | Additional CORS origins (comma-separated) |
| `HOST` | No | "0.0.0.0" | Server bind address |
| `PORT` | No | 8000 | Server port |

## Deployment
- Railway auto-deploys from `main` branch on GitHub push
- Service account email: `vila-acadia-bot@vila-acadia.iam.gserviceaccount.com` (must have Editor access to the Google Sheet)
- For risky changes, create a branch, push it, switch Railway to deploy from that branch for testing, then merge to `main`

## Known Limitations
- Manager auth uses plain text password (no hashing, no JWT)
- No rate limiting on auth endpoints
- No audit logging for submissions
- Currency is ₪ (Israeli Shekel) throughout the UI
