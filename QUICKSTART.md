# Quick Start Guide

This guide will get you up and running with the Vila Acadia backend in under 5 minutes.

## Step 1: Install Dependencies

```bash
# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

## Step 2: Configure Google Sheets

### Create Your Google Sheet

1. Create a new Google Sheet
2. Rename the first tab to **"Settings"**
3. Add these headers in row 1: `Name` | `PIN`
4. Add test employees:
   - Row 2: `John Doe` | `1234`
   - Row 3: `Jane Smith` | `5678`

### Get Service Account Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (or use existing)
3. Enable **Google Sheets API**
4. Create a **Service Account**:
   - IAM & Admin → Service Accounts
   - Create Service Account
   - Click on it → Keys → Add Key → Create New Key → JSON
5. Download the JSON file
6. **Share your Google Sheet** with the service account email (found in the JSON as `client_email`)

## Step 3: Configure Environment

Copy the `.env.example` to `.env` (if you see the file) or create a new `.env` file:

```env
# Get this from your sheet URL: https://docs.google.com/spreadsheets/d/THIS_PART_IS_THE_ID/edit
GOOGLE_SHEET_ID=your_sheet_id_here

# Copy the ENTIRE JSON content from your service account file and paste as ONE line
SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"...","private_key":"..."}

# Optional
HOST=0.0.0.0
PORT=8000
```

**Important:** The `SERVICE_ACCOUNT_JSON` must be the complete JSON on a single line.

## Step 4: Run the Server

```bash
# Option 1: Using uvicorn directly
uvicorn src.backend.main:app --reload --host 0.0.0.0 --port 8000

# Option 2: Using the run script
python -m src.backend.run
```

## Step 5: Test the API

Open your browser to:

1. **Interactive API Docs:** http://localhost:8000/docs
2. **Health Check:** http://localhost:8000/health

### Test Authentication

In the API docs (http://localhost:8000/docs):

1. Click on `POST /auth/verify`
2. Click "Try it out"
3. Enter:
   ```json
   {
     "name": "John Doe",
     "pin": "1234"
   }
   ```
4. Click "Execute"
5. You should see a successful response!

## Troubleshooting

### "Failed to connect to Google Sheets"
- ✓ Check your `GOOGLE_SHEET_ID` is correct
- ✓ Verify the sheet is shared with the service account email
- ✓ Ensure `SERVICE_ACCOUNT_JSON` is valid JSON (no line breaks)

### "Settings tab not found"
- ✓ Create a tab named exactly "Settings" (case-sensitive)
- ✓ Add "Name" and "PIN" headers

### Import errors
- ✓ Make sure you're in the virtual environment (`venv\Scripts\activate`)
- ✓ Run `pip install -r requirements.txt` again

## Next Steps

Your backend is now running! The system includes:

✅ PIN authentication  
✅ Google Sheets integration  
✅ Health check endpoint  
✅ Duplicate entry prevention  
✅ Automatic monthly sheet creation  

See `README.md` for full documentation and deployment instructions.


