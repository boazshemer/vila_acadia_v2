# Unified Deployment Changes - Summary

## What Changed?

Your Vila Acadia application has been restructured from **two separate deployments** (frontend + backend) into **one unified deployment** that serves both from a single instance.

## Before vs After

### Before (Separate Deployments) ❌
```
┌─────────────────┐         ┌─────────────────┐
│   Frontend      │         │    Backend      │
│   (Vercel/      │  CORS   │   (Railway)     │
│   Netlify)      │ ───────▶│                 │
│   Port 3000     │ Issues  │   Port 8000     │
└─────────────────┘         └─────────────────┘
   example.com              api.example.com
```

**Problems:**
- Two separate deployments to manage
- CORS configuration needed
- Two different URLs
- More complex setup
- Double the deployment cost

### After (Unified) ✅
```
┌────────────────────────────────────┐
│      Single Service (Railway)       │
│                                     │
│  ┌──────────┐    ┌──────────┐     │
│  │ Frontend │    │ Backend  │     │
│  │ (Static) │◀───│ (FastAPI)│     │
│  └──────────┘    └──────────┘     │
│                                     │
└────────────────────────────────────┘
        vila-acadia.railway.app
```

**Benefits:**
- ✅ Single deployment
- ✅ No CORS issues
- ✅ One URL for everything
- ✅ Simpler management
- ✅ Lower cost
- ✅ Faster (same-origin requests)

## Technical Changes

### 1. Dockerfile Updated

**Old:** Only built backend
```dockerfile
FROM python:3.11-slim
# Only Python dependencies
# Only backend code
```

**New:** Multi-stage build for both
```dockerfile
# Stage 1: Build frontend
FROM node:20-slim as frontend-builder
RUN npm run build  # Creates static files

# Stage 2: Build Python dependencies
FROM python:3.11-slim as python-builder
# Install Python packages

# Stage 3: Combine everything
FROM python:3.11-slim
COPY --from=frontend-builder /frontend/dist ./static
COPY backend code
# FastAPI serves both!
```

### 2. FastAPI Backend Updated (`src/backend/main.py`)

**Added:**
- Static file serving for frontend
- Catch-all route for React Router
- Assets mounting

```python
# Mount static files (after all API routes)
app.mount("/assets", StaticFiles(directory="static/assets"))

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    # Serve index.html for client-side routing
    return FileResponse("static/index.html")
```

**API routes unchanged** - all your existing endpoints work the same!

### 3. Frontend Config Updated (`src/frontend/src/services/api.js`)

**Old:**
```javascript
const API_BASE_URL = '/api';  // Always use proxy
```

**New:**
```javascript
// Development: Use '/api' (proxied by Vite)
// Production: Use '' (same origin, no proxy needed)
const API_BASE_URL = import.meta.env.MODE === 'development' ? '/api' : '';
```

### 4. Documentation Added

New files:
- ✅ `UNIFIED_DEPLOYMENT.md` - Comprehensive deployment guide
- ✅ `DEPLOY_NOW.md` - Quick 5-minute deploy guide
- ✅ `CHANGES_UNIFIED_DEPLOYMENT.md` - This file

Updated:
- ✅ `DEPLOYMENT.md` - Updated for unified approach

## File Changes Summary

```
Modified:
  ✏️  Dockerfile                          (multi-stage build)
  ✏️  src/backend/main.py                 (static file serving)
  ✏️  src/frontend/src/services/api.js    (environment-aware API URL)
  ✏️  src/frontend/vite.config.js         (build config)
  ✏️  DEPLOYMENT.md                       (updated instructions)

Added:
  ✨  UNIFIED_DEPLOYMENT.md               (comprehensive guide)
  ✨  DEPLOY_NOW.md                       (quick start)
  ✨  CHANGES_UNIFIED_DEPLOYMENT.md       (this file)
```

## How to Deploy

### If You Already Have Deployments

1. **Delete the old frontend deployment** (Vercel/Netlify/Railway)
2. **Keep or update the backend deployment** with new code
3. **Push changes** to GitHub
4. Railway will rebuild automatically

### Fresh Deployment

See `DEPLOY_NOW.md` for 5-minute quick start!

```bash
# Push to GitHub
git push origin main

# Railway auto-deploys
# Or use CLI: railway up
```

## Environment Variables

**No changes needed!** Same variables as before:
- `GOOGLE_SHEET_ID` ✅
- `SERVICE_ACCOUNT_JSON` ✅
- `MANAGER_PASSWORD` ✅

## Testing

### Local Development (No Change)

**Frontend:**
```bash
cd src/frontend
npm install
npm run dev
```
Runs on http://localhost:3000

**Backend:**
```bash
python -m uvicorn src.backend.main:app --reload
```
Runs on http://localhost:8000

Vite proxy forwards `/api/*` to backend automatically.

### Production (Unified)

After deploying to Railway:

1. **Access frontend:** `https://your-app.railway.app`
2. **Test API:** `https://your-app.railway.app/health`
3. **API docs:** `https://your-app.railway.app/docs`

All from the same URL!

## Migration Checklist

- [x] ✅ Dockerfile updated for multi-stage build
- [x] ✅ FastAPI configured to serve static files
- [x] ✅ Frontend API configuration updated
- [x] ✅ Documentation updated

**Ready to deploy!**

## Troubleshooting

### "I still see CORS errors"

This means you might be accessing the old frontend deployment. Make sure you're using the Railway URL only.

### "Frontend not loading"

1. Check Railway logs: `railway logs`
2. Look for "Building frontend..." in logs
3. Verify build completed successfully
4. Check if `static/` directory exists

### "API calls fail"

1. Check browser console (F12) → Network tab
2. Verify requests go to same domain (no cross-origin)
3. Check Railway logs for backend errors

### "Build fails on Railway"

1. Ensure all files are committed: `git status`
2. Check `src/frontend/package.json` exists
3. Check `requirements.txt` exists
4. View Railway build logs for specific error

## Benefits Recap

| Aspect | Before | After |
|--------|--------|-------|
| **Deployments** | 2 separate | 1 unified |
| **URLs** | 2 different | 1 single |
| **CORS** | Required | Not needed |
| **Cost** | 2× services | 1× service |
| **Complexity** | Higher | Lower |
| **Setup Time** | ~15 min | ~5 min |
| **Maintenance** | 2 services | 1 service |

## What Stays the Same?

- ✅ All API endpoints (no changes)
- ✅ All frontend functionality (no changes)
- ✅ Google Sheets integration (no changes)
- ✅ Environment variables (same ones)
- ✅ Development workflow (same process)
- ✅ Database structure (no changes)

## Next Steps

1. **Deploy** using `DEPLOY_NOW.md`
2. **Test** all functionality
3. **Share** new URL with team
4. **Delete** old frontend deployment
5. **Update** any bookmarks/links

## Questions?

- 📖 See `UNIFIED_DEPLOYMENT.md` for detailed guide
- 🚀 See `DEPLOY_NOW.md` for quick start
- 📝 See `DEPLOYMENT.md` for Railway specifics
- 🔍 Check Railway logs: `railway logs`

---

**This is a better architecture!** Enjoy simpler deployments. 🎉

