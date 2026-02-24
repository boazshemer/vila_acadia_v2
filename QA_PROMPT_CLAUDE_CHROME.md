# QA Testing Prompt for Claude Chrome — Vila Acadia

Copy the prompt below and paste it into Claude Chrome to run a full QA test.

---

## PROMPT START

You are a QA tester for a restaurant employee timesheet & tip distribution web app called "Vila Acadia". Your job is to systematically test every button, form, link, and flow in the app, and then verify the data actually reached the Google Sheets database.

### App Info
- **App URL:** https://vilaacadiav2-production.up.railway.app/
- **Google Sheets URL:** https://docs.google.com/spreadsheets/d/15Jk59DA3IXGKf9x3s5jvkn2tPVtfGAc5yihuIYZokJ4/edit?gid=0#gid=0
- **Today's date:** 2026-02-22

The app has 4 pages:
1. `/` — Employee Login
2. `/employee/time-entry` — Employee Time Entry (after login)
3. `/manager` — Manager Login
4. `/manager/dashboard` — Manager Dashboard (after login)

---

### PHASE 1: Basic Load & Health Check

1. **Navigate to the app URL** (https://vilaacadiav2-production.up.railway.app/)
2. **Verify the page loads** — you should see an "Employee Login" page with:
   - A user icon at the top
   - Title: "Employee Login"
   - Subtitle: "Enter your name and PIN to continue"
   - A "Your Name" text input field
   - A "4-Digit PIN" password input field
   - A "Log In" button (should be DISABLED initially since PIN is empty)
   - A footer text: "Are you a manager? Click here"
3. **Check the health endpoint** — navigate to https://vilaacadiav2-production.up.railway.app/health
   - Should return JSON with `"status": "connected"` and a valid `spreadsheet_id`
   - This confirms the backend is running and connected to Google Sheets
4. Go back to the main page.

**Report:** Does the page load? Is the design clean and not broken? Is the health endpoint OK?

---

### PHASE 2: Employee Login — Validation Tests

Test these scenarios on the Employee Login page (`/`):

5. **Empty name submit** — leave name empty, type any 4-digit PIN, try to click "Log In"
   - Expected: The button should be disabled OR a toast error "Please enter your name" should appear

6. **Short PIN** — type a name, enter only 2-3 digits in PIN
   - Expected: "Log In" button should stay DISABLED (it enables only when PIN has exactly 4 digits)

7. **Non-numeric PIN** — try typing letters in the PIN field
   - Expected: The field should only accept digits (letters are filtered out)

8. **Wrong credentials** — type a name like "FAKE USER" and PIN "0000", click "Log In"
   - Expected: A red toast error appears: "Invalid credentials" or similar. No page navigation.

9. **Correct credentials** — First, go to the Google Sheets URL and check the "Settings" tab to find a real employee name and their PIN. Then come back to the app and log in with those credentials.
   - Expected: A green toast "Welcome, [name]!" appears, and you are redirected to `/employee/time-entry`

**Report:** Do all validations work? Does correct login redirect properly?

---

### PHASE 3: Employee Time Entry — Full Flow

After logging in as an employee, you should be on `/employee/time-entry`:

10. **Verify page layout:**
    - Header shows "Submit Hours" and "Welcome, [employee name]!"
    - A "Logout" button in the top right
    - A form with: Date picker, Start Time, End Time
    - Quick time buttons under Start Time: "9 AM", "5 PM", "Now"
    - Quick time buttons under End Time: "5 PM", "11 PM", "Now"
    - A "Total Hours" calculated display (should show 0.00 initially)
    - A "Submit Hours" button (DISABLED when hours = 0)
    - A blue info box saying you can only submit once per day

11. **Test quick time buttons:**
    - Click "9 AM" under Start Time → Start Time field should fill with 09:00
    - Click "5 PM" under End Time → End Time field should fill with 17:00
    - The "Total Hours" display should now show **8.00 hours**
    - The "Submit Hours" button should now be ENABLED

12. **Test "Now" buttons:**
    - Click "Now" under Start Time → should fill with current time
    - Click "Now" under End Time → should fill with current time

13. **Test hours calculation:**
    - Set start time to 09:00, end time to 17:00 → should show 8.00 hours
    - Set start time to 22:00, end time to 06:00 → should show 8.00 hours (overnight shift) AND show a warning "This appears to be an overnight shift"

14. **Test date picker:**
    - The date should default to today (2026-02-22)
    - You should NOT be able to select a future date (max is today)
    - Try changing the date to yesterday or another past date — it should be allowed

15. **Submit hours:**
    - Set date to today, start time 09:00, end time 17:00
    - Click "Submit Hours"
    - Expected: Loading spinner appears on the button, then a green toast: "Successfully submitted 8.0 hours for 2026-02-22"
    - The form should reset (times cleared, date back to today)
    - **IMPORTANT:** If you get an error "already submitted" — that's OK, it means this date was already tested. Try a different date (e.g., 2026-02-21).

16. **Verify in Google Sheets:**
    - Go to the Google Sheets URL
    - Check the tab named "02-2026" (February 2026)
    - Find the date column matching the date you submitted (look at row 9 for date headers)
    - Find the employee's row (rows 10-79)
    - Verify the hours value (e.g., 8) appears in the HOURS column for that date
    - The adjacent date column should have a tip formula (or be empty if tips weren't submitted yet)

17. **Test duplicate submission:**
    - Go back to the app and try to submit hours for the SAME date again
    - Expected: An error toast should appear (the system prevents overwriting)

18. **Test logout:**
    - Click the "Logout" button
    - Expected: Green toast "Logged out successfully", redirected back to Employee Login (`/`)

**Report:** Do quick buttons work? Is hours calculation correct? Does submission succeed and show in Google Sheets? Does duplicate prevention work? Does logout work?

---

### PHASE 4: Manager Login — Validation & Auth

19. **Navigate to manager login:**
    - From the Employee Login page, click "Click here" in the footer (next to "Are you a manager?")
    - Expected: You are on `/manager` — Manager Login page

20. **Verify manager login page layout:**
    - A "← Back to Employee Login" link at the top
    - A shield icon
    - Title: "Manager Access"
    - Subtitle: "Enter manager password to continue"
    - A password input field
    - An amber/orange "Access Manager Dashboard" button

21. **Test "Back to Employee Login" link:**
    - Click "← Back to Employee Login"
    - Expected: Redirected back to `/` (Employee Login)
    - Navigate back to `/manager`

22. **Test empty password:**
    - Leave password empty, try to submit
    - Expected: Error toast "Please enter password" or HTML validation prevents submission

23. **Test wrong password:**
    - Type "wrongpassword", click "Access Manager Dashboard"
    - Expected: Red toast "Incorrect password" or "Invalid password". Password field clears.

24. **Test correct password:**
    - The manager password is configured on the backend. Try common passwords or check with the owner.
    - If you don't know the password, report that you cannot proceed with manager testing.
    - Expected on success: Green toast "Manager access granted", redirect to `/manager/dashboard`

**Report:** Does navigation to manager login work? Do validation errors show correctly? Does correct login redirect?

---

### PHASE 5: Manager Dashboard — Full Flow

After logging in as manager, you should be on `/manager/dashboard`:

25. **Verify page layout:**
    - Header: Shield icon + "Manager Dashboard"
    - Subtitle: "Submit daily tips and manage employees"
    - A "Logout" button
    - LEFT card: "Submit Daily Tips" with:
      - Date picker (defaults to today, max is today)
      - "Total Tips Amount" number input
      - "Calculate & Submit" amber button
    - RIGHT card: "Employee List" with:
      - Currently shows "Employee list will appear here" (this is a known TODO)
      - Text: "Employees are managed in the Google Sheets Settings tab"
    - Bottom info box: explains dynamic tip split (95/5 when 1 T member, 90/10 when 2+)

26. **Test tip preview:**
    - Type 500 in the Total Tips Amount field
    - Expected: A yellow preview box appears showing "$500.00" and text about distribution

27. **Test tip amount validation:**
    - Clear the tips field and try to submit
    - Expected: Error "Please enter a valid tip amount"
    - Enter 0 or negative number
    - Expected: Error "Please enter a valid tip amount"

28. **Submit daily tips:**
    - Set date to a date that has employee hours submitted (use the same date from phase 3)
    - Enter a tip amount (e.g., 500)
    - Click "Calculate & Submit"
    - Expected: Loading spinner, then green toast like "Tips submitted! Formulas calculated for X employees"
    - Form resets

29. **Verify tips in Google Sheets:**
    - Go to the Google Sheets URL, tab "02-2026"
    - Find the date column for the date you submitted tips
    - **Row 2 (TOTAL TIP):** Should show the tip amount you entered (e.g., 500)
    - **Row 3 (TOTAL TIP E):** Should show formula result = total * 0.95 (if 1 T member worked, e.g., 475) or total * 0.9 (if 2+ T members, e.g., 450)
    - **Row 4 (TOTAL TIP T):** Should show formula result = total * 0.05 (if 1 T member worked, e.g., 25) or total * 0.1 (if 2+ T members, e.g., 50)
    - **Row 5 (TOTAL HOUR E):** Should show total hours for E-type employees
    - **Row 6 (TOTAL HOUR T):** Should show total hours for T-type employees
    - **Row 7 (TIP PER HOUR E):** Should show per-hour tip rate for employees
    - **Row 8 (TIP PER HOUR T):** Should show per-hour tip rate for team members
    - **Employee rows (10-79):** Each employee should have a tip payout formula in the DATE column (their hours × tip-per-hour for their type)
    - **TOTAL MONTHLY TIPS column** (rightmost): Should sum all tip payouts per employee across all dates. Has light blue formatting.

30. **Test manager logout:**
    - Click "Logout" button
    - Expected: Green toast "Logged out successfully", redirect to `/manager` login

**Report:** Does tip submission work end-to-end? Do formulas appear correctly in Google Sheets? Is the dynamic tip split correct (95/5 when 1 T member works, 90/10 when 2+)?

---

### PHASE 6: Navigation & Edge Cases

31. **Direct URL access without auth:**
    - Open `/employee/time-entry` directly without logging in
    - Expected: Red toast "Please log in first", redirect to `/`
    - Open `/manager/dashboard` directly without logging in
    - Expected: Red toast "Please log in first", redirect to `/manager`

32. **Unknown route:**
    - Navigate to `/random-page` or any non-existent route
    - Expected: Redirect to `/` (Employee Login)

33. **Mobile responsiveness:**
    - Resize browser window to mobile width (~375px)
    - Check all 4 pages look good and buttons are usable
    - Forms should stack vertically on mobile

34. **Concurrent quick interactions:**
    - On time entry page, rapidly click "Submit Hours" multiple times
    - Expected: Button should be disabled during loading (prevents double submission)

---

### PHASE 7: Google Sheets Data Integrity

35. **Open the Google Sheets** and perform these checks:
    - **Settings tab:** Has columns for Name, PIN, and Type (E or T)
    - **02-2026 tab:**
      - Row 1 is empty
      - Row 9 has headers: "שם העובד" (employee name), "סוג" (type), "HOURS", then date pairs
      - Each date has TWO columns: HOURS + date (dd/mm/yyyy format)
      - The rightmost column is "TOTAL MONTHLY TIPS" with light blue background
      - Formulas in rows 2-8 calculate correctly (no #REF! or #ERROR! values)
      - Employee data rows (10-79) have correct hours and tip calculations

---

## TEST RESULTS SUMMARY

Please provide a summary table:

| Test # | Test Name | Status (PASS/FAIL) | Notes |
|--------|-----------|-------------------|-------|
| 1-4 | Page Load & Health | | |
| 5-9 | Employee Login Validation | | |
| 10-18 | Employee Time Entry | | |
| 19-24 | Manager Login | | |
| 25-30 | Manager Dashboard & Tips | | |
| 31-34 | Navigation & Edge Cases | | |
| 35 | Google Sheets Integrity | | |

**Total buttons/interactive elements tested:**
- Employee Login: 2 inputs + 1 submit button + 1 navigation link = **4**
- Employee Time Entry: 3 inputs + 6 quick-time buttons + 1 submit button + 1 logout button = **11**
- Manager Login: 1 input + 1 submit button + 1 back link = **3**
- Manager Dashboard: 2 inputs + 1 submit button + 1 logout button = **4**
- **Total: 22 interactive elements across 4 pages**

**API endpoints tested:**
1. `GET /health` — health check
2. `POST /auth/verify` — employee login
3. `POST /submit-hours` — submit employee hours
4. `POST /manager/auth` — manager login
5. `POST /manager/submit-daily-tip` — submit daily tips
- **Total: 5 endpoints**

List any bugs found, UI issues, or unexpected behaviors.

## PROMPT END
