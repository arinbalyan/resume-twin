# Supabase Setup Guide for Resume Twin Platform

## 🚀 Complete Setup Instructions

### **Step 1: Create Supabase Project**

1. **Go to**: https://app.supabase.com
2. **Sign up/Login** with your account
3. **Click**: "New Project"
4. **Fill details**:
   - Name: `resume-twin-platform`
   - Database Password: Generate a strong password
   - Region: Choose closest to your users
5. **Click**: "Create new project"
6. **Wait**: For project to be fully provisioned (2-3 minutes)

### **Step 2: Get Your Project Credentials**

After project is created, go to **Settings** → **API**:

```
PROJECT URL: https://your-project-ref.supabase.co
ANON KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SERVICE_ROLE_KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### **Step 3: Setup Database Schema**

1. **Go to**: SQL Editor in Supabase Dashboard
2. **Copy & paste** the complete `schema.sql` file content
3. **Click**: "Run" to execute
4. **Verify**: All tables are created (check Table Editor)

### **Step 4: Enable Authentication**

1. **Go to**: Authentication → Settings
2. **Enable providers**:
   - ✅ Email (already enabled)
   - ✅ Google OAuth (optional)
   - ✅ GitHub OAuth (optional)
3. **Configure Site URL**: 
   - Development: `http://localhost:3000`
   - Production: `https://yourdomain.com`

### **Step 5: Setup Storage (S3-like functionality)**

1. **Go to**: Storage
2. **Create bucket**: `portfolio-files`
3. **Set bucket policies**:
   ```sql
   -- Public access for portfolio images
   CREATE POLICY "Public files are viewable by everyone" ON storage.objects FOR SELECT USING (bucket_id = 'portfolio-files');
   
   -- Users can upload their own files
   CREATE POLICY "Users can upload their own files" ON storage.objects FOR INSERT WITH CHECK (bucket_id = 'portfolio-files' AND auth.uid()::text = (storage.foldername(name))[1]);
   ```

### **Step 6: Configure Row Level Security**

Your schema.sql already includes RLS policies. Make sure they're active:

1. **Check**: Each table has RLS enabled
2. **Verify**: Policies are working in your app

### **Step 7: Get OpenRouter API Key**

1. **Go to**: https://openrouter.ai
2. **Sign up/Login**
3. **Go to**: Keys section
4. **Create new key** or use existing
5. **Copy**: Your API key

### **Step 8: Environment Variables Setup**

#### **Backend (.env file)**
```bash
# Copy from backend/.env.example and fill these:
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_ANON_KEY=your-anon-key
DATABASE_URL=postgresql://postgres:[password]@db.your-project-ref.supabase.co:5432/postgres

# S3 (Supabase Storage)
AWS_ACCESS_KEY_ID=[Get from Supabase Storage settings]
AWS_SECRET_ACCESS_KEY=[Get from Supabase Storage settings]
AWS_S3_BUCKET=portfolio-files
AWS_S3_REGION=us-east-1

# OpenRouter
OPENROUTER_API_KEY=your-openrouter-key

# Other settings...
SECRET_KEY=your-super-secure-secret-key
```

#### **Frontend (.env.local file)**
Create `frontend/.env.local`:
```bash
# Supabase Configuration
VITE_SUPABASE_URL=https://your-project-ref.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key

# API Base URL
VITE_API_URL=http://localhost:8000/api

# OpenRouter (for client-side AI features if needed)
VITE_OPENROUTER_API_KEY=your-openrouter-key
```

### **Step 9: Test the Connection**

#### **Backend Test**:
```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### **Frontend Test**:
```bash
cd frontend
npm install
npm run dev
```

### **Step 10: Verify Everything Works**

1. **Open**: http://localhost:3000
2. **Check**: No console errors
3. **Try**: Registration (should create Supabase auth user)
4. **Test**: Profile creation
5. **Verify**: Files upload to Supabase Storage

## 🛠️ Troubleshooting

### **Common Issues:**

1. **RLS Policies blocking access**:
   - Check policies in Supabase Dashboard → Authentication → Policies
   - Test with anon key first

2. **Storage access denied**:
   - Verify bucket policies are correctly set
   - Check Storage is enabled in your project

3. **Database connection failed**:
   - Verify DATABASE_URL format
   - Test connection with psql or Supabase CLI

4. **API errors 401/403**:
   - Check API keys are correct
   - Verify CORS settings in backend

### **Useful Supabase CLI Commands** (Optional):

```bash
# Install Supabase CLI
npm install -g supabase

# Login to Supabase
supabase login

# Link your project
supabase link --project-ref your-project-ref

# Generate types
supabase gen types typescript --local > frontend/src/types/supabase.ts
```

## 🔐 Security Best Practices

1. **Never commit .env files** to git
2. **Use service role key only** on backend
3. **Keep anon key public** (it's safe to expose)
4. **Enable RLS** on all user tables
5. **Test policies** thoroughly
6. **Use HTTPS** in production
7. **Rotate API keys** regularly

## 📊 Database Schema Overview

Your database includes:
- **User Profiles** (extends Supabase auth.users)
- **Education History**
- **Project Portfolio**
- **Professional Experience** (certifications, internships, courses)
- **Resume Management** with AI optimization
- **File Uploads** with secure storage
- **Templates** with ratings system

All tables have proper **RLS policies**, **indexes**, and **triggers** for security and performance.

---

**🎉 You're all set! Your Resume Twin Platform is ready for development!**