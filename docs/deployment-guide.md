# Resume Twin Platform - Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the Resume Twin platform to production environments. The platform consists of:

- **Frontend**: React application (Vite + Tailwind CSS v4)
- **Backend**: FastAPI application (Python 3.11+)
- **Database**: PostgreSQL (via Supabase)
- **Storage**: S3-compatible storage (Supabase Storage)
- **AI Services**: OpenRouter API integration

## Prerequisites

### Required Services

1. **Supabase Account** (Database + Storage + Auth)
   - Sign up at https://supabase.com
   - Create a new project
   - Note your project URL and keys

2. **OpenRouter API Key** (AI Services)
   - Sign up at https://openrouter.ai
   - Generate API key
   - Fund account for AI model usage

3. **Deployment Platform** (Choose one)
   - Railway.app (recommended for backend)
   - Vercel (recommended for frontend)
   - Heroku
   - AWS/GCP/Azure

### Required Tools

- Node.js 18+ and npm/pnpm
- Python 3.11+
- Docker and Docker Compose (for local development)
- Git

## Environment Configuration

### Backend Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Project Information
PROJECT_NAME=Resume Twin API
VERSION=1.0.0
ENVIRONMENT=production
DEBUG=false

# Security
SECRET_KEY=<generate-secure-random-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=10080

# Database (Supabase)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
DATABASE_URL=postgresql://postgres:password@db.your-project.supabase.co:5432/postgres

# Supabase Storage
SUPABASE_STORAGE_ACCESS_KEY=your-storage-access-key
SUPABASE_STORAGE_SECRET_KEY=your-storage-secret-key
SUPABASE_STORAGE_BUCKET=portfolio-files
SUPABASE_STORAGE_REGION=us-east-1
SUPABASE_STORAGE_URL=https://your-project.supabase.co/storage/v1

# AI Services
OPENROUTER_API_KEY=your-openrouter-api-key
OPENROUTER_MODEL=anthropic/claude-3-sonnet
AI_TIMEOUT_SECONDS=30
AI_MAX_RETRIES=3

# CORS
BACKEND_CORS_ORIGINS=https://your-frontend-domain.com,http://localhost:5173

# File Upload
MAX_FILE_SIZE=10485760
ALLOWED_FILE_TYPES=pdf,jpg,jpeg,png,doc,docx

# LaTeX
LATEX_COMPILATION_TIMEOUT=30

# Monitoring (Optional)
SENTRY_DSN=your-sentry-dsn
LOG_LEVEL=INFO
```

### Frontend Environment Variables

Create a `.env.production` file in the `frontend/` directory:

```env
VITE_API_BASE_URL=https://your-backend-api.com/api/v1
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
VITE_APP_NAME=Resume Twin
VITE_APP_VERSION=1.0.0
```

## Database Setup

### 1. Initialize Supabase Database

```bash
# Navigate to your Supabase project
# Go to SQL Editor and run the schema

cd database
cat schema.sql | psql <your-supabase-connection-string>
```

Or use the Supabase dashboard:
1. Go to SQL Editor
2. Copy contents of `database/schema.sql`
3. Execute the SQL

### 2. Verify Tables Created

Check that all tables are created:
- profiles
- education
- projects
- project_media
- project_technologies
- certifications
- internships
- courses
- activities
- templates
- resume_versions
- optimization_history
- file_uploads

### 3. Enable Row Level Security (RLS)

RLS policies are included in the schema. Verify they are enabled:

```sql
SELECT schemaname, tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
AND rowsecurity = true;
```

## Backend Deployment

### Option 1: Railway.app (Recommended)

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login and Initialize**
   ```bash
   railway login
   cd backend
   railway init
   ```

3. **Configure Environment Variables**
   ```bash
   railway variables set SECRET_KEY=<your-secret>
   railway variables set SUPABASE_URL=<your-url>
   # ... set all required variables
   ```

4. **Deploy**
   ```bash
   railway up
   ```

5. **Get Deployment URL**
   ```bash
   railway domain
   ```

### Option 2: Docker Container

1. **Build Docker Image**
   ```bash
   cd backend
   docker build -t resume-twin-backend .
   ```

2. **Run Container**
   ```bash
   docker run -d \
     --name resume-twin-api \
     -p 8000:8000 \
     --env-file .env \
     resume-twin-backend
   ```

3. **Push to Container Registry**
   ```bash
   docker tag resume-twin-backend your-registry/resume-twin-backend:latest
   docker push your-registry/resume-twin-backend:latest
   ```

### Option 3: Manual Server Deployment

1. **Setup Python Environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run with Gunicorn**
   ```bash
   gunicorn app.main:app \
     --workers 4 \
     --worker-class uvicorn.workers.UvicornWorker \
     --bind 0.0.0.0:8000 \
     --timeout 120
   ```

3. **Setup Supervisor (Process Manager)**
   ```ini
   [program:resume-twin-api]
   directory=/path/to/backend
   command=/path/to/venv/bin/gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   autostart=true
   autorestart=true
   stderr_logfile=/var/log/resume-twin/api.err.log
   stdout_logfile=/var/log/resume-twin/api.out.log
   ```

4. **Setup Nginx Reverse Proxy**
   ```nginx
   server {
       listen 80;
       server_name api.your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

## Frontend Deployment

### Option 1: Vercel (Recommended)

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login and Deploy**
   ```bash
   cd frontend
   vercel login
   vercel --prod
   ```

3. **Configure Environment Variables in Vercel Dashboard**
   - Go to your project settings
   - Add all `VITE_*` variables
   - Redeploy

### Option 2: Netlify

1. **Install Netlify CLI**
   ```bash
   npm install -g netlify-cli
   ```

2. **Build and Deploy**
   ```bash
   cd frontend
   npm run build
   netlify deploy --prod
   ```

3. **Configure `netlify.toml`**
   ```toml
   [build]
     command = "npm run build"
     publish = "dist"

   [[redirects]]
     from = "/*"
     to = "/index.html"
     status = 200
   ```

### Option 3: Static Hosting (S3/CloudFlare)

1. **Build Application**
   ```bash
   cd frontend
   npm run build
   ```

2. **Upload to S3**
   ```bash
   aws s3 sync dist/ s3://your-bucket-name --delete
   ```

3. **Configure CloudFront Distribution**
   - Point to S3 bucket
   - Set default root object: `index.html`
   - Configure error pages to redirect to `index.html`

## Post-Deployment Configuration

### 1. Update CORS Origins

Update backend environment:
```env
BACKEND_CORS_ORIGINS=https://your-frontend.vercel.app,https://your-custom-domain.com
```

### 2. Setup Custom Domain

**Frontend (Vercel):**
```bash
vercel domains add your-domain.com
```

**Backend (Railway):**
```bash
railway domain add api.your-domain.com
```

### 3. Configure SSL Certificates

Most platforms (Vercel, Railway, Netlify) provide automatic SSL.

For manual setups:
```bash
# Using Let's Encrypt
certbot --nginx -d your-domain.com -d api.your-domain.com
```

### 4. Setup Monitoring

**Sentry Integration:**
```bash
# Backend
pip install sentry-sdk

# Frontend
npm install @sentry/react @sentry/tracing
```

**Configure Sentry:**
```python
# backend/app/main.py
import sentry_sdk
sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    traces_sample_rate=1.0,
    environment=settings.ENVIRONMENT
)
```

## Verification Checklist

- [ ] Backend API is accessible at production URL
- [ ] Frontend loads correctly
- [ ] Database migrations completed
- [ ] Environment variables configured
- [ ] CORS settings allow frontend domain
- [ ] File uploads work correctly
- [ ] AI optimization endpoints functional
- [ ] SSL certificates installed
- [ ] Custom domains configured
- [ ] Monitoring/logging setup
- [ ] Backup strategy implemented

## Health Checks

### Backend Health Check
```bash
curl https://api.your-domain.com/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production"
}
```

### Frontend Health Check
```bash
curl https://your-domain.com
```

Should return the HTML of your app.

## Backup and Disaster Recovery

### Database Backups

Supabase provides automatic backups. Additionally:

```bash
# Manual backup
pg_dump <supabase-connection-string> > backup-$(date +%Y%m%d).sql

# Automated daily backups
0 2 * * * /usr/bin/pg_dump <connection-string> > /backups/resume-twin-$(date +\%Y\%m\%d).sql
```

### File Storage Backups

```bash
# Sync Supabase storage to local backup
aws s3 sync s3://supabase-storage-bucket/ ./backups/storage/
```

### Application Code Backups

Use Git tags for releases:
```bash
git tag -a v1.0.0 -m "Production release 1.0.0"
git push origin v1.0.0
```

## Scaling Considerations

### Backend Scaling

- **Horizontal Scaling**: Add more API server instances
- **Load Balancing**: Use platform load balancer or Nginx
- **Database Connection Pooling**: Configure in Supabase
- **Caching**: Implement Redis for frequently accessed data

### Frontend Scaling

- **CDN**: Use CloudFlare or similar
- **Image Optimization**: Optimize and compress images
- **Code Splitting**: Already configured with Vite
- **Lazy Loading**: Implement for heavy components

## Security Best Practices

1. **Never commit `.env` files to Git**
2. **Rotate secrets regularly**
3. **Use HTTPS everywhere**
4. **Implement rate limiting**
5. **Enable RLS on all Supabase tables**
6. **Validate all user inputs**
7. **Keep dependencies updated**
8. **Monitor for security vulnerabilities**

## Monitoring and Maintenance

### Application Monitoring

- Setup Sentry for error tracking
- Configure uptime monitoring (UptimeRobot, Pingdom)
- Monitor API response times
- Track database query performance

### Log Management

- Centralize logs (Papertrail, LogDNA)
- Set up log retention policies
- Monitor for errors and warnings

### Performance Monitoring

- Track API endpoint performance
- Monitor database query times
- Measure frontend load times
- Set up alerts for degraded performance

## Troubleshooting

### Common Issues

**Issue: CORS errors**
```
Solution: Verify BACKEND_CORS_ORIGINS includes your frontend domain
```

**Issue: Database connection failures**
```
Solution: Check DATABASE_URL and Supabase credentials
```

**Issue: File upload failures**
```
Solution: Verify S3/Supabase Storage credentials and bucket permissions
```

**Issue: AI optimization not working**
```
Solution: Verify OPENROUTER_API_KEY and check API credits
```

## Support and Documentation

- **API Documentation**: https://api.your-domain.com/docs
- **User Guide**: https://docs.your-domain.com
- **GitHub Repository**: https://github.com/your-org/resume-twin
- **Support Email**: support@your-domain.com

## Rollback Procedure

If deployment fails:

1. **Revert to previous version**
   ```bash
   # Railway
   railway rollback

   # Vercel
   vercel rollback
   ```

2. **Restore database from backup**
   ```bash
   psql <connection-string> < backup-YYYYMMDD.sql
   ```

3. **Verify application health**
   ```bash
   curl https://api.your-domain.com/api/v1/health
   ```

## Continuous Integration/Deployment

### GitHub Actions Example

```yaml
name: Deploy Production

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Railway
        run: railway up
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Vercel
        run: vercel --prod
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
```

## Next Steps

After successful deployment:

1. Setup monitoring and alerting
2. Configure automated backups
3. Implement analytics tracking
4. Setup user feedback system
5. Plan for future feature releases

---

**Last Updated**: November 30, 2025
**Version**: 1.0.0
