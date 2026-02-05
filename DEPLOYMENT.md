# Deployment Guide - Railway (Full Stack)

This guide covers deploying the **complete Vila Acadia application** (frontend + backend) to Railway as a single unified service.

## Prerequisites

- Railway account (sign up at https://railway.app)
- Google Cloud Service Account credentials
- Google Sheet ID

## Option 1: Deploy via Railway CLI

### 1. Install Railway CLI

```bash
# Using npm
npm install -g @railway/cli

# Or using curl (macOS/Linux)
sh -c "$(curl -sSL https://raw.githubusercontent.com/railwayapp/cli/master/install.sh)"
```

### 2. Login to Railway

```bash
railway login
```

### 3. Initialize Project

From your project root directory:

```bash
railway init
```

Follow the prompts to create a new project or link to an existing one.

### 4. Add Environment Variables

Add your environment variables via the Railway CLI:

```bash
railway variables set GOOGLE_SHEET_ID="your_sheet_id_here"
railway variables set SERVICE_ACCOUNT_JSON='{"type":"service_account","project_id":"..."}'
```

Or add them through the Railway dashboard (recommended for the JSON):

1. Go to your project on railway.app
2. Click on your service
3. Go to the "Variables" tab
4. Add:
   - `GOOGLE_SHEET_ID`: Your Google Sheet ID
   - `SERVICE_ACCOUNT_JSON`: Full JSON content (paste as raw JSON)

### 5. Deploy

```bash
railway up
```

Railway will automatically:
- Detect Python
- Install dependencies from `requirements.txt`
- Use the start command from `Procfile`

### 6. Get Your URL

```bash
railway domain
```

Or visit the Railway dashboard to see your deployed URL.

## Option 2: Deploy via GitHub Integration

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit - Backend foundation"
git remote add origin <your-repo-url>
git push -u origin main
```

### 2. Connect to Railway

1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway will auto-detect the configuration

### 3. Add Environment Variables

1. In the Railway dashboard, click on your service
2. Go to "Variables" tab
3. Add:
   - `GOOGLE_SHEET_ID`
   - `SERVICE_ACCOUNT_JSON`

### 4. Deploy

Railway will automatically deploy when you push to GitHub.

## Configuration Files

The project includes these deployment configurations:

### `Dockerfile`
Multi-stage build that:
1. **Stage 1**: Builds the React frontend using Node.js (npm run build)
2. **Stage 2**: Installs Python backend dependencies
3. **Stage 3**: Combines built frontend and backend into final image

The frontend is built into static files and served by FastAPI.

### `Procfile`
Defines the web server start command:
```
web: uvicorn src.backend.main:app --host 0.0.0.0 --port $PORT
```

### `runtime.txt`
Specifies Python version:
```
python-3.11
```

## Architecture

**Single Service Deployment:**
- Frontend (React/Vite) is built to static files during Docker build
- Backend (FastAPI) serves both:
  - API endpoints at `/auth/verify`, `/health`, `/submit-hours`, etc.
  - Frontend static files at `/` (root and all non-API routes)
- No CORS issues since everything runs on the same domain
- Simplified deployment and management

## Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `GOOGLE_SHEET_ID` | Yes | Google Sheet ID from URL | `1abc...xyz` |
| `SERVICE_ACCOUNT_JSON` | Yes | Complete service account JSON | `{"type":"service_account",...}` |
| `HOST` | No | Server host (Railway sets this) | `0.0.0.0` |
| `PORT` | No | Server port (Railway sets this) | `8000` |

**Note:** Railway automatically provides the `PORT` environment variable. The application uses this when deployed.

## Verify Deployment

After deployment, test your endpoints:

### Health Check

```bash
curl https://your-app.railway.app/health
```

Expected response:
```json
{
  "status": "connected",
  "spreadsheet_id": "your_sheet_id",
  "spreadsheet_title": "Your Sheet Name",
  "message": "Successfully connected to Google Sheets"
}
```

### Authentication Test

```bash
curl -X POST https://your-app.railway.app/auth/verify \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "pin": "1234"}'
```

### Frontend Access

Visit: `https://your-app.railway.app`

The complete web application will be available at the root URL with all pages:
- `/` - Landing/Login page
- `/employee/login` - Employee login
- `/employee/time-entry` - Time entry form
- `/manager/login` - Manager login
- `/manager/dashboard` - Manager dashboard

### API Documentation

Visit: `https://your-app.railway.app/docs`

## Troubleshooting

### Build Fails

**Issue:** Dependencies not installing

**Solution:** 
- Check `requirements.txt` syntax
- Verify Python version in `runtime.txt`
- Check Railway build logs

### Connection Errors

**Issue:** "Failed to connect to Google Sheets"

**Solution:**
1. Verify `GOOGLE_SHEET_ID` is correct
2. Check `SERVICE_ACCOUNT_JSON` is valid (test locally first)
3. Ensure Google Sheet is shared with service account
4. Check Railway logs: `railway logs`

### 503 Service Unavailable

**Issue:** Health check returns 503

**Solution:**
1. Check Google Sheets API quotas in Google Cloud Console
2. Verify service account permissions
3. Check Railway logs for detailed errors

### Application Crashes

**Issue:** App restarts continuously

**Solution:**
1. Check Railway logs: `railway logs`
2. Test locally with same environment variables
3. Verify all required env vars are set
4. Check for typos in variable names

## Monitoring

### View Logs

```bash
# Using CLI
railway logs

# Or in Railway dashboard
Project → Service → Deployments → View Logs
```

### Monitor Performance

Railway dashboard provides:
- CPU usage
- Memory usage
- Network traffic
- Request metrics

## Updating the Deployment

### Using CLI

```bash
# Make changes to your code
git add .
git commit -m "Update: description"
git push

# If using direct Railway deployment
railway up
```

### Auto-deployment (GitHub)

Once connected via GitHub, Railway automatically deploys on every push to your main branch.

## Rollback

If a deployment fails:

1. Go to Railway dashboard
2. Click on your service
3. Go to "Deployments" tab
4. Find a previous successful deployment
5. Click "Redeploy"

## Security Best Practices

1. **Never commit `.env` files** - Use `.gitignore`
2. **Rotate service account keys** periodically
3. **Use Railway's secret management** for sensitive data
4. **Enable Railway's built-in DDoS protection**
5. **Monitor logs** for suspicious activity

## Costs

Railway offers:
- Free tier: $5 credit/month
- Pay-as-you-go: ~$5-20/month for typical usage

Monitor usage in the Railway dashboard.

## Support

- Railway Discord: https://discord.gg/railway
- Railway Docs: https://docs.railway.app
- Project Issues: [Create an issue in your repo]

---

**Next Steps After Deployment:**
1. Test all endpoints
2. Set up custom domain (optional)
3. Configure CORS for your frontend domain
4. Set up monitoring/alerting
5. Document your production URL for the frontend team


