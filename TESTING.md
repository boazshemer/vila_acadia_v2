# Testing Guide

This guide provides comprehensive testing procedures for the Vila Acadia backend.

## Setup Testing Environment

### 1. Create Test Google Sheet

1. Create a new Google Sheet named "Vila Acadia Test"
2. Create a "Settings" tab with test data:

| Name | PIN |
|------|-----|
| Test User 1 | 1111 |
| Test User 2 | 2222 |
| Admin Test | 9999 |

3. Share with your service account email
4. Copy the Sheet ID from the URL

### 2. Configure Test Environment

Create a `.env.test` file:

```env
GOOGLE_SHEET_ID=your_test_sheet_id
SERVICE_ACCOUNT_JSON={"type":"service_account",...}
HOST=0.0.0.0
PORT=8000
```

## Manual Testing

### Test 1: Server Startup

**Objective:** Verify server starts without errors

```bash
uvicorn src.backend.main:app --reload
```

**Expected Output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
✓ Connected to Google Sheets
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Pass Criteria:**
- ✓ No error messages
- ✓ "Connected to Google Sheets" message appears
- ✓ Server accessible at http://localhost:8000

---

### Test 2: Root Endpoint

**Objective:** Verify API information endpoint

```bash
curl http://localhost:8000/
```

**Expected Response:**
```json
{
  "service": "Vila Acadia Timesheet API",
  "version": "1.0.0",
  "status": "running",
  "endpoints": {
    "health": "/health",
    "auth": "/auth/verify",
    "docs": "/docs"
  }
}
```

**Pass Criteria:**
- ✓ Status code: 200
- ✓ Returns JSON with service info
- ✓ All endpoint paths listed

---

### Test 3: Health Check - Success

**Objective:** Verify Google Sheets connectivity

```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "connected",
  "spreadsheet_id": "your_sheet_id",
  "spreadsheet_title": "Vila Acadia Test",
  "message": "Successfully connected to Google Sheets"
}
```

**Pass Criteria:**
- ✓ Status code: 200
- ✓ Status: "connected"
- ✓ Correct spreadsheet ID
- ✓ Spreadsheet title retrieved

---

### Test 4: Health Check - Failure

**Objective:** Verify error handling for connection issues

**Setup:** Temporarily set wrong `GOOGLE_SHEET_ID` in `.env`

```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "detail": "Failed to connect: ..."
}
```

**Pass Criteria:**
- ✓ Status code: 503 (Service Unavailable)
- ✓ Error message in detail field
- ✓ Server doesn't crash

**Cleanup:** Restore correct `GOOGLE_SHEET_ID`

---

### Test 5: Authentication - Valid Credentials

**Objective:** Verify successful PIN authentication

```bash
curl -X POST http://localhost:8000/auth/verify \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User 1", "pin": "1111"}'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Authentication successful",
  "employee_name": "Test User 1"
}
```

**Pass Criteria:**
- ✓ Status code: 200
- ✓ success: true
- ✓ Employee name returned correctly

---

### Test 6: Authentication - Invalid PIN

**Objective:** Verify authentication rejection for wrong PIN

```bash
curl -X POST http://localhost:8000/auth/verify \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User 1", "pin": "9999"}'
```

**Expected Response:**
```json
{
  "success": false,
  "message": "Invalid credentials. Please check your name and PIN.",
  "employee_name": ""
}
```

**Pass Criteria:**
- ✓ Status code: 200 (returns response, not error)
- ✓ success: false
- ✓ No employee name returned

---

### Test 7: Authentication - Invalid Name

**Objective:** Verify authentication rejection for non-existent user

```bash
curl -X POST http://localhost:8000/auth/verify \
  -H "Content-Type: application/json" \
  -d '{"name": "Non Existent", "pin": "1111"}'
```

**Expected Response:**
```json
{
  "success": false,
  "message": "Invalid credentials. Please check your name and PIN.",
  "employee_name": ""
}
```

**Pass Criteria:**
- ✓ Status code: 200
- ✓ success: false
- ✓ Same error message (doesn't reveal which field is wrong)

---

### Test 8: Authentication - Case Insensitivity

**Objective:** Verify name matching is case-insensitive

```bash
curl -X POST http://localhost:8000/auth/verify \
  -H "Content-Type: application/json" \
  -d '{"name": "TEST USER 1", "pin": "1111"}'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Authentication successful",
  "employee_name": "TEST USER 1"
}
```

**Pass Criteria:**
- ✓ Status code: 200
- ✓ success: true (case doesn't matter)
- ✓ Authentication succeeds

---

### Test 9: Authentication - Invalid PIN Format

**Objective:** Verify validation for non-numeric PIN

```bash
curl -X POST http://localhost:8000/auth/verify \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User 1", "pin": "abcd"}'
```

**Expected Response:**
```json
{
  "detail": [
    {
      "loc": ["body", "pin"],
      "msg": "PIN must contain only digits",
      "type": "value_error"
    }
  ]
}
```

**Pass Criteria:**
- ✓ Status code: 422 (Validation Error)
- ✓ Error indicates PIN must be digits

---

### Test 10: Authentication - Wrong PIN Length

**Objective:** Verify validation for incorrect PIN length

```bash
curl -X POST http://localhost:8000/auth/verify \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User 1", "pin": "123"}'
```

**Expected Response:**
```json
{
  "detail": [
    {
      "loc": ["body", "pin"],
      "msg": "String should have at least 4 characters",
      "type": "string_too_short"
    }
  ]
}
```

**Pass Criteria:**
- ✓ Status code: 422 (Validation Error)
- ✓ Error indicates PIN length requirement

---

### Test 11: Monthly Sheet Auto-Creation

**Objective:** Verify automatic creation of monthly sheets

**Python Test Script:**

```python
from src.backend.gsheets_service import gs_service
from datetime import datetime

# This should create "January 2026" sheet if it doesn't exist
worksheet = gs_service.get_or_create_month_sheet()

print(f"Sheet name: {worksheet.title}")
print(f"Headers: {worksheet.row_values(1)}")
```

**Expected Output:**
```
Sheet name: January 2026
Headers: ['Employee', 'Date', 'Clock In', 'Clock Out', 'Hours Worked', 'Tips Collected', 'Tip Rate (per hour)', 'Payout']
```

**Pass Criteria:**
- ✓ New sheet created with current month name
- ✓ All 8 headers present in correct order
- ✓ Headers formatted (bold, gray background)

---

### Test 12: Duplicate Entry Check

**Objective:** Verify read-before-write safety guard

**Python Test Script:**

```python
from src.backend.gsheets_service import gs_service

# First check - should not exist
exists, row = gs_service.check_entry_exists("Test User 1", "2026-01-28")
print(f"First check - Exists: {exists}, Row: {row}")

# Manually add entry to sheet at row 2:
# Test User 1 | 2026-01-28 | 09:00 | 17:00 | 8 | ...

# Second check - should exist
exists, row = gs_service.check_entry_exists("Test User 1", "2026-01-28")
print(f"Second check - Exists: {exists}, Row: {row}")
```

**Expected Output:**
```
First check - Exists: False, Row: None
Second check - Exists: True, Row: 2
```

**Pass Criteria:**
- ✓ Returns False when entry doesn't exist
- ✓ Returns True and row number when entry exists
- ✓ Correctly identifies employee + date combination

---

## Interactive Testing (API Docs)

### Access Swagger UI

1. Start the server
2. Open http://localhost:8000/docs
3. Test each endpoint interactively

**Endpoints to Test:**
- ✓ GET / (root)
- ✓ GET /health
- ✓ POST /auth/verify

### Test Cases in Swagger UI

1. **Successful Auth:**
   - name: "Test User 1"
   - pin: "1111"

2. **Failed Auth:**
   - name: "Test User 1"
   - pin: "0000"

3. **Validation Error:**
   - name: "Test User 1"
   - pin: "abc" (should fail validation)

---

## Google Sheets Verification

### Manual Sheet Checks

1. **Settings Sheet:**
   - ✓ Tab named "Settings" exists
   - ✓ Has "Name" and "PIN" columns
   - ✓ Contains test employee data

2. **Monthly Sheet (after auto-creation):**
   - ✓ New tab created (e.g., "January 2026")
   - ✓ Has all 8 column headers
   - ✓ Headers are bold and styled
   - ✓ Ready to accept data entries

3. **Permissions:**
   - ✓ Service account email has Editor access
   - ✓ API can read from Settings
   - ✓ API can create new sheets/tabs

---

## Error Scenarios

### Test Error Handling

1. **Missing Settings Tab:**
   - Delete "Settings" tab from sheet
   - Try health check
   - Should return error message

2. **Malformed Settings Data:**
   - Remove "Name" or "PIN" column from Settings
   - Try authentication
   - Should handle gracefully

3. **Network Issues:**
   - Disconnect internet
   - Try health check
   - Should timeout gracefully with proper error

4. **Invalid Service Account:**
   - Use wrong credentials
   - Server should fail to start with clear error

---

## Performance Testing

### Basic Load Test (Optional)

Using Apache Bench (ab):

```bash
# Test health endpoint
ab -n 100 -c 10 http://localhost:8000/health

# Test auth endpoint
ab -n 100 -c 10 -p auth.json -T "application/json" http://localhost:8000/auth/verify
```

Create `auth.json`:
```json
{"name": "Test User 1", "pin": "1111"}
```

**Expected:**
- All requests succeed
- No 5xx errors
- Reasonable response times (< 1s per request)

---

## Test Checklist

Before marking Phase 1 complete, verify:

### Core Functionality
- [ ] Server starts without errors
- [ ] Google Sheets connection successful
- [ ] Health check returns correct status
- [ ] Root endpoint returns API info

### Authentication
- [ ] Valid credentials accepted
- [ ] Invalid credentials rejected
- [ ] Case-insensitive name matching works
- [ ] PIN validation works (4 digits only)
- [ ] Proper error messages returned

### Google Sheets Integration
- [ ] Can read Settings sheet
- [ ] Can parse employee data correctly
- [ ] Monthly sheets auto-create
- [ ] Headers formatted correctly
- [ ] Duplicate check logic works

### Error Handling
- [ ] Graceful handling of missing sheets
- [ ] Proper HTTP status codes
- [ ] Clear error messages
- [ ] No server crashes on errors

### Documentation
- [ ] API docs accessible at /docs
- [ ] All endpoints documented
- [ ] Request/response models clear

---

## Next Steps After Testing

1. ✅ All tests pass → Ready for deployment
2. ❌ Tests fail → Review logs, fix issues, retest
3. Document any issues found
4. Update PROJECT_STATE.md with test results

---

## Reporting Issues

When reporting test failures, include:

1. Test number and name
2. Expected vs actual behavior
3. Error messages/logs
4. Environment details (OS, Python version)
5. Screenshot (if relevant)

---

**Test Environment Cleanup:**

After testing, you may want to:
- Delete test entries from Google Sheet
- Archive test monthly sheets
- Keep Settings sheet for future tests


