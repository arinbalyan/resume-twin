# 🚀 Resume Twin - Quick Start Guide

## ✅ Current Status

Both servers are running successfully:
- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:3001

## 🔐 Getting Started

### Create Your Account

1. Go to: **http://localhost:3001/register**
2. Fill in your details:
   - Email address
   - Password (minimum 6 characters)
   - Confirm password
3. Click **"Create Account"**
4. You'll be redirected to login

## 🎯 How to Use

### 1. Login

1. Go to: **http://localhost:3001/login**
2. Enter your credentials (email and password)
3. Click **"Sign in"**
4. You'll be redirected to the dashboard!

### 2. Access Dashboard

After login, you'll be redirected to: http://localhost:3001/dashboard

### 3. Explore Features

- **Profile**: Manage your profile information
- **Projects**: Add and showcase your projects
- **Resume**: Generate AI-optimized resumes
- **Settings**: Configure your preferences

## 🔧 Backend API

### API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Test API Endpoint

```powershell
# Health check
curl http://localhost:8000/health

# Get API info
curl http://localhost:8000/
```

## 📊 Supabase Configuration

All authentication is handled by Supabase:

- **Project URL**: https://ndzgiivakcskuqhrhwww.supabase.co
- **Dashboard**: https://app.supabase.com/project/ndzgiivakcskuqhrhwww

### Configured Services

✅ **Supabase Auth** - User authentication & authorization  
✅ **Supabase Database** - PostgreSQL database  
✅ **Supabase Storage** - File storage for resumes & images  
✅ **Row Level Security** - Data protection  

## 🎨 Frontend Features

- ✅ Modern React 18 with TypeScript
- ✅ Tailwind CSS v4 for styling
- ✅ Supabase Authentication integration
- ✅ React Router for navigation
- ✅ React Hook Form for form validation
- ✅ Hot Toast notifications
- ✅ Responsive design

## 🔒 Security

- All passwords are hashed by Supabase
- JWT tokens for authentication
- Auto-refresh tokens
- Session persistence
- CORS protection
- Row Level Security in database

## 🛠️ Development

### Backend (Already Running)

```powershell
cd backend
uv run python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (Already Running)

```powershell
cd frontend
npm run dev
```

### Stop Servers

Press `Ctrl + C` in the terminal windows

## 📝 Next Steps

1. ✅ Create admin user (see instructions above)
2. ✅ Login to the application
3. 📝 Complete your profile
4. 📝 Add your projects and experience
5. 📝 Generate your first AI-optimized resume
6. 📝 Explore analytics and insights

## 🐛 Troubleshooting

### Can't Login?

1. Make sure you created the user first
2. Check that both servers are running
3. Verify Supabase credentials in `.env` files
4. Check browser console for errors (F12)

### Backend Not Responding?

```powershell
# Check if backend is running
curl http://localhost:8000/health

# Restart backend
cd backend
uv run python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Not Loading?

```powershell
# Check if frontend is running
# Should see: Local: http://localhost:3000/

# Restart frontend
cd frontend
npm run dev
```

## 📚 Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)

## 🎉 You're All Set!

The application is fully functional and ready to use. Enjoy building your professional portfolio and AI-optimized resumes!

---

**Support**: If you encounter any issues, check the terminal logs for error messages.
