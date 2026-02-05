# Unified Deployment Guide

## Overview

The Vila Acadia application is now configured as a **unified full-stack deployment** where:
- Frontend (React/Vite) and Backend (FastAPI) run as a **single service**
- Frontend is built into static files during deployment
- Backend serves both API endpoints and frontend files
- No CORS issues (same origin)
- Simplified management

## How It Works

### Build Process (Docker Multi-Stage)

**Stage 1: Frontend Build**
```dockerfile
FROM node:20-slim as frontend-builder
# Install npm dependencies
# Build React app (npm run build)
# Output: dist/ folder with static files
```

**Stage 2: Python Dependencies**
```dockerfile
FROM python:3.11-slim as python-builder
# Install Python packages from requirements.txt
```

**Stage 3: Final Runtime**
```dockerfile
FROM python:3.11-slim
# Copy Python dependencies
# Copy backend code (src/backend/)
# Copy built frontend (dist/ → static/)
# Run: uvicorn src.backend.main:app
```

### Runtime Behavior

**FastAPI serves:**
1. **API endpoints** (priority):
   - `/health` - Health check
   - `/auth/verify` - Authentication
   - `/submit-hours` - Time submission
   - `/manager/*` - Manager endpoints
   - `/docs` - API documentation

2. **Static files** (catch-all):
   - `/` → `static/index.html`
   - `/assets/*` → `static/assets/*`
   - Any other route → `static/index.html` (for React Router)

## Deployment to Railway

### Method 1: Via Railway CLI

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login**
   ```bash
   railway login
   ```

3. **Initialize Project**
   ```bash
   railway init
   ```

4. **Set Environment Variables**
   ```bash
   railway variables set GOOGLE_SHEET_ID="your_sheet_id"
   railway variables set SERVICE_ACCOUNT_JSON='{"type":"service_account",...}'
   railway variables set MANAGER_PASSWORD="your_secure_password"
   ```

5. **Deploy**
   ```bash
   railway up
   ```

6. **Get URL**
   ```bash
   railway domain
   ```

### Method 2: Via GitHub (Recommended)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Unified deployment setup"
   git push origin main
   ```

2. **Connect Railway**
   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will auto-detect the Dockerfile

3. **Configure Environment Variables**
   In Railway dashboard → Variables:
   - `GOOGLE_SHEET_ID` - Your Google Sheet ID
   - `SERVICE_ACCOUNT_JSON` - Full JSON (paste as single line)
   - `MANAGER_PASSWORD` - Manager password

4. **Deploy**
   Railway automatically builds and deploys on push to main

### Method 3: Docker Locally

To test the unified deployment locally:

```bash
# Build the Docker image
docker build -t vila-acadia .

# Run the container
docker run -p 8000:8000 \
  -e GOOGLE_SHEET_ID="your_sheet_id" \
  -e SERVICE_ACCOUNT_JSON='{"type":"service_account",...}' \
  -e MANAGER_PASSWORD="your_password" \
  vila-acadia

# Access at http://localhost:8000
```

## Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `GOOGLE_SHEET_ID` | Yes | Google Sheet ID | `1abc...xyz` |
| `SERVICE_ACCOUNT_JSON` | Yes | Service account credentials | `{"type":"service_account",...}` |
| `MANAGER_PASSWORD` | Yes | Manager dashboard password | `SecurePass123!` |
| `PORT` | No | Server port (Railway sets this) | `8000` |
| `HOST` | No | Server host | `0.0.0.0` |

## Verification

After deployment, verify everything works:

### 1. Health Check
```bash
curl https://your-app.railway.app/health
```

Expected: `{"status":"connected",...}`

### 2. Frontend Access
Visit: `https://your-app.railway.app`

You should see the landing page with login options.

### 3. Employee Login Flow
1. Click "Employee Login"
2. Enter name and PIN
3. Submit hours

### 4. Manager Dashboard
1. Go to `/manager/login`
2. Enter manager password
3. Access dashboard

### 5. API Documentation
Visit: `https://your-app.railway.app/docs`

Interactive API documentation should load.

## Troubleshooting

### Frontend Not Loading

**Symptom:** 404 errors or blank page

**Check:**
1. View Railway logs: `railway logs`
2. Verify static files were built:
   ```bash
   # In Railway logs, look for:
   # "Building frontend..."
   # "✓ built in 5.23s"
   ```
3. Check if `static/` directory exists in container

**Solution:**
- Ensure `src/frontend/package.json` has `"build": "vite build"`
- Verify `src/frontend/vite.config.js` has correct output directory

### API Endpoints Not Working

**Symptom:** Frontend loads but API calls fail

**Check:**
1. Browser console (F12) for network errors
2. Railway logs for backend errors
3. Environment variables are set correctly

**Solution:**
- Verify GOOGLE_SHEET_ID is correct
- Check SERVICE_ACCOUNT_JSON is valid JSON
- Ensure Google Sheet is shared with service account email

### CORS Errors (Shouldn't Happen)

**Symptom:** CORS errors in browser console

**This indicates:** Frontend and backend are NOT on the same domain

**Solution:**
- You might have separate deployments still running
- Delete the old frontend deployment
- Use only the unified deployment URL

### Build Failures

**Symptom:** Railway build fails

**Check logs for:**
1. **"npm: not found"** → Dockerfile issue
2. **"requirements.txt: not found"** → File missing
3. **"Module not found"** → Python/Node dependency issue

**Solution:**
- Verify Dockerfile is correct (see repo)
- Check all files are committed to git
- Ensure `requirements.txt` and `package.json` are present

## Development vs Production

### Development (Local)

Frontend: `cd src/frontend && npm run dev` (port 3000)
Backend: `cd src/backend && python -m uvicorn main:app --reload` (port 8000)

Frontend uses Vite proxy to forward `/api/*` to backend.

### Production (Railway)

Single unified service (port 8000):
- API calls go directly to same domain (no proxy needed)
- FastAPI serves both API and static files
- Single container, single URL

## Monitoring

### View Logs
```bash
# CLI
railway logs --tail

# Or in Railway Dashboard
Project → Service → Deployments → Logs
```

### Key Log Messages

**Successful Startup:**
```
✓ Connected to Google Sheets successfully
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Frontend Served:**
```
INFO:     127.0.0.1:52154 - "GET / HTTP/1.1" 200 OK
INFO:     127.0.0.1:52154 - "GET /assets/index-abc123.js HTTP/1.1" 200 OK
```

**API Calls:**
```
INFO:     127.0.0.1:52154 - "POST /auth/verify HTTP/1.1" 200 OK
```

## Updating the Application

1. **Make changes locally**
2. **Test locally** (frontend dev server + backend)
3. **Commit changes**
   ```bash
   git add .
   git commit -m "Description of changes"
   ```
4. **Push to GitHub**
   ```bash
   git push origin main
   ```
5. **Railway auto-deploys** (if GitHub integration enabled)

Or use CLI:
```bash
railway up
```

## Rollback

If deployment breaks:

1. Go to Railway Dashboard
2. Project → Service → Deployments
3. Find previous successful deployment
4. Click "Redeploy"

## Cost Estimation

**Railway Pricing:**
- Free tier: $5 credit/month
- Typical usage: $5-15/month
- Includes:
  - 512 MB RAM
  - 1 GB storage
  - Unlimited bandwidth (fair use)

**Monitor usage:** Railway Dashboard → Usage

## Security Checklist

- [ ] `.env` file is in `.gitignore`
- [ ] `SERVICE_ACCOUNT_JSON` stored as Railway variable (not in code)
- [ ] Manager password is strong and unique
- [ ] Google Sheet shared only with service account
- [ ] Railway's built-in HTTPS enabled
- [ ] Regular monitoring of logs for suspicious activity

## Next Steps

After successful deployment:

1. **Custom Domain** (optional)
   - Railway Dashboard → Service → Settings → Domains
   - Add custom domain and configure DNS

2. **Monitoring**
   - Set up Railway notification webhooks
   - Monitor error rates in logs

3. **Backup**
   - Google Sheets auto-saves
   - Consider exporting data periodically

4. **Team Training**
   - Share deployment URL with team
   - Test login flow with actual employee credentials
   - Train manager on dashboard usage

## Support

- **Railway:** [discord.gg/railway](https://discord.gg/railway)
- **Docs:** [docs.railway.app](https://docs.railway.app)
- **Logs:** Always check `railway logs` first

---

**Congratulations!** You now have a unified, production-ready deployment. 🚀

