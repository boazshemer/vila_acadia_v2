# Deploy Now - Quick Start

Get your Vila Acadia app deployed to Railway in **5 minutes**!

## Prerequisites

✅ Railway account ([railway.app](https://railway.app))
✅ Google Sheet set up (see main README.md)
✅ Service account JSON credentials

## Option 1: Deploy from GitHub (Easiest) ⭐

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/vila-acadia.git
git push -u origin main
```

### Step 2: Deploy to Railway

1. Go to [railway.app](https://railway.app) and login
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize GitHub and select your repository
5. Railway will automatically detect the Dockerfile and start building

### Step 3: Add Environment Variables

While it's building, add your environment variables:

1. Click on your service in Railway
2. Go to **"Variables"** tab
3. Click **"New Variable"** and add:

```
GOOGLE_SHEET_ID=1abc123xyz...
```

```
SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"..."}
```

```
MANAGER_PASSWORD=YourSecurePassword123
```

**Tip:** For SERVICE_ACCOUNT_JSON, paste the entire JSON as a single line.

### Step 4: Get Your URL

1. Go to **"Settings"** tab
2. Scroll to **"Networking"**
3. Click **"Generate Domain"**
4. Copy your URL: `https://your-app.railway.app`

### Step 5: Test It!

Visit your URL and you should see the Vila Acadia login page! 🎉

## Option 2: Deploy via CLI

### Step 1: Install Railway CLI

```bash
npm install -g @railway/cli
```

### Step 2: Login and Initialize

```bash
railway login
railway init
```

### Step 3: Set Environment Variables

```bash
railway variables set GOOGLE_SHEET_ID="your_sheet_id_here"
railway variables set SERVICE_ACCOUNT_JSON='{"type":"service_account",...}'
railway variables set MANAGER_PASSWORD="YourSecurePassword"
```

### Step 4: Deploy

```bash
railway up
```

### Step 5: Generate Domain

```bash
railway domain
```

## Verify Deployment

### 1. Health Check
```bash
curl https://your-app.railway.app/health
```

Should return: `{"status":"connected",...}`

### 2. Open in Browser
```
https://your-app.railway.app
```

You should see the landing page with "Employee Login" and "Manager Portal" buttons.

### 3. Test Login

**Employee:**
1. Click "Employee Login"
2. Enter name: `John Doe` (or your actual employee name)
3. Enter PIN: `1234` (or your actual PIN)
4. Should navigate to time entry form

**Manager:**
1. Visit `/manager/login`
2. Enter the password you set in `MANAGER_PASSWORD`
3. Should see the dashboard

## Common Issues

### ❌ "Failed to connect to Google Sheets"

**Fix:**
1. Check `GOOGLE_SHEET_ID` is correct
2. Verify `SERVICE_ACCOUNT_JSON` is valid (no line breaks)
3. Ensure Google Sheet is shared with service account email:
   - Open your Google Sheet
   - Click "Share"
   - Add service account email (from JSON: `client_email` field)
   - Give "Editor" access

### ❌ "Invalid credentials" when logging in

**Fix:**
1. Check the "Settings" tab in your Google Sheet
2. Verify employee name and PIN match exactly
3. Check Railway logs: `railway logs`

### ❌ Frontend shows 404

**Fix:**
1. Check Railway logs for build errors
2. Ensure `src/frontend/` exists with `package.json`
3. Redeploy: `railway up` or push to GitHub again

### ❌ Build fails

**Fix:**
1. View logs in Railway Dashboard
2. Common issues:
   - Missing `package.json` in `src/frontend/`
   - Missing `requirements.txt` in root
   - Invalid Dockerfile syntax
3. Verify all files are committed: `git status`

## What Just Happened?

Railway just:
1. 🔨 Built your frontend (React app) into static files
2. 🐍 Installed Python backend dependencies
3. 📦 Combined everything into one Docker container
4. 🚀 Deployed to a public URL
5. 🔄 Set up auto-deploy on future git pushes

Now you have:
- ✅ Public URL for your app
- ✅ Automatic HTTPS
- ✅ Auto-scaling
- ✅ Auto-deploy on push (if using GitHub)

## Next Steps

1. **Share the URL** with your team
2. **Add actual employees** to Google Sheet Settings tab
3. **Test the full workflow:**
   - Employee logs in
   - Submits hours
   - Manager enters daily tips
   - Check calculations in Google Sheet

4. **Custom Domain** (optional):
   - Railway Dashboard → Settings → Domains
   - Add your domain and update DNS

5. **Monitor:**
   ```bash
   railway logs --tail
   ```

## Cost

- **Free tier:** $5 credit/month
- **Expected usage:** ~$5-15/month
- **Monitor:** Railway Dashboard → Usage tab

## Get Help

- Railway logs: `railway logs`
- Railway Discord: [discord.gg/railway](https://discord.gg/railway)
- Check `UNIFIED_DEPLOYMENT.md` for detailed troubleshooting

---

**You're done!** Your app is live. 🎉

Share your Railway URL with your team and start tracking hours!

