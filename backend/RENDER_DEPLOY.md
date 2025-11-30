# Render Deployment Guide - Resume Twin Backend

## Quick Deploy to Render Free Tier

### Prerequisites
1. A [Render account](https://render.com) (free)
2. A [Supabase account](https://supabase.com) (free tier available)
3. An [OpenRouter account](https://openrouter.ai) (free tier available)

### Step 1: Fork/Clone the Repository

```bash
git clone https://github.com/your-username/resume-twin.git
cd resume-twin
```

### Step 2: Deploy to Render

#### Option A: One-Click Deploy (Recommended)

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New** → **Web Service**
3. Connect your GitHub repository
4. Select the `backend` directory as the root
5. Render will auto-detect the settings from `render.yaml`

#### Option B: Manual Deploy

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New** → **Web Service**
3. Connect your GitHub repo
4. Configure:
   - **Name**: `resume-twin-api`
   - **Region**: Oregon (free tier)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements-render.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Step 3: Configure Environment Variables

In Render Dashboard → Your Service → **Environment**:

#### Required Variables

| Variable | Description | Where to get it |
|----------|-------------|-----------------|
| `SUPABASE_URL` | Your Supabase project URL | Supabase Dashboard → Settings → API |
| `SUPABASE_KEY` | Supabase anon/public key | Supabase Dashboard → Settings → API |
| `OPENROUTER_API_KEY` | OpenRouter API key | [openrouter.ai/keys](https://openrouter.ai/keys) |

#### Recommended Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `ENVIRONMENT` | `production` | Production mode |
| `DEBUG` | `false` | Disable debug features |
| `MEMORY_OPTIMIZED` | `true` | Enable memory optimizations |
| `BACKEND_CORS_ORIGINS` | `https://your-frontend.vercel.app` | Your frontend URL |

#### Optional Variables (for enhanced features)

| Variable | Description |
|----------|-------------|
| `GITHUB_TOKEN` | GitHub API for repo imports |
| `PDFSHIFT_API_KEY` | Cloud PDF generation |
| `SENTRY_DSN` | Error tracking |

### Step 4: Verify Deployment

1. Wait for the build to complete (~2-5 minutes)
2. Visit your service URL: `https://resume-twin-api.onrender.com`
3. Check health endpoint: `https://resume-twin-api.onrender.com/health`

Expected response:
```json
{
  "status": "healthy",
  "database": "healthy",
  "version": "0.1.0",
  "environment": "production"
}
```

---

## Free Tier Limitations & Optimizations

### Render Free Tier Limits
- **RAM**: 512MB
- **CPU**: Shared
- **Spin-down**: Service sleeps after 15 minutes of inactivity
- **Cold starts**: ~30-60 seconds after sleep

### How We Handle These

1. **Memory Optimization**
   - Single worker process
   - Minimal dependencies (`requirements-render.txt`)
   - No heavy packages (WeasyPrint, LaTeX, Celery)

2. **Cold Start Mitigation**
   - Lightweight `/ping` endpoint for external uptime monitors
   - Fast initialization (no heavy modules on startup)

3. **PDF Generation**
   - Uses cloud PDF services instead of local rendering
   - Falls back to ReportLab for basic PDFs

### Keeping Your Service Warm

To prevent cold starts, set up a free uptime monitor:

1. **UptimeRobot** (free): [uptimerobot.com](https://uptimerobot.com)
   - Monitor: `https://your-service.onrender.com/ping`
   - Interval: Every 5 minutes

2. **Cron-job.org** (free): [cron-job.org](https://cron-job.org)
   - URL: `https://your-service.onrender.com/ping`
   - Schedule: Every 5 minutes

---

## Troubleshooting

### Service won't start

1. Check Render logs for errors
2. Verify all required environment variables are set
3. Ensure `SUPABASE_URL` doesn't have trailing slash

### Database connection errors

```
Error: Supabase client not configured
```

**Solution**: Verify `SUPABASE_URL` and `SUPABASE_KEY` are set correctly.

### Out of memory errors

```
Error: Process killed - out of memory
```

**Solutions**:
1. Ensure `MEMORY_OPTIMIZED=true`
2. Check you're using `requirements-render.txt`
3. Consider upgrading to paid tier ($7/month)

### Slow responses after inactivity

This is normal for free tier. The first request after sleep takes 30-60 seconds.

**Solutions**:
1. Set up an uptime monitor (see above)
2. Upgrade to paid tier for always-on service

---

## Upgrading to Production

When ready to scale, consider:

1. **Render Starter ($7/month)**
   - Always-on (no sleep)
   - 512MB RAM
   - Better performance

2. **Add Redis (optional)**
   - Enable caching
   - Session storage
   - Rate limiting

3. **Add full PDF support**
   - Use `requirements.txt` instead of `requirements-render.txt`
   - Enables local LaTeX/WeasyPrint rendering

---

## File Structure for Render

```
backend/
├── render.yaml              # Render blueprint config
├── Dockerfile.render        # Optimized Docker image
├── requirements-render.txt  # Minimal dependencies
├── start.sh                 # Start script
├── .env.render.example      # Environment template
└── app/
    └── ...
```

---

## Support

- **Render Docs**: [render.com/docs](https://render.com/docs)
- **Supabase Docs**: [supabase.com/docs](https://supabase.com/docs)
- **OpenRouter Docs**: [openrouter.ai/docs](https://openrouter.ai/docs)
