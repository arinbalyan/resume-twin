# Resume Twin Platform - Development Setup Script (PowerShell)
Write-Host "🚀 Setting up Resume Twin Platform development environment..." -ForegroundColor Green

# Check prerequisites
Write-Host "📋 Checking prerequisites..." -ForegroundColor Yellow

# Check Node.js
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js is required but not installed. Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

# Check Python
try {
    $pythonVersion = python --version
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python 3 is required but not installed. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Install Astral UV
try {
    $uvVersion = uv --version
    Write-Host "✅ Astral UV found: $uvVersion" -ForegroundColor Green
} catch {
    Write-Host "📦 Installing Astral UV..." -ForegroundColor Yellow
    $installUrl = "https://astral.sh/uv/install.sh"
    Write-Host "Please run manually: Invoke-WebRequest -Uri $installUrl -OutFile install-uv.ps1; .\install-uv.ps1" -ForegroundColor Yellow
    Write-Host "Then restart PowerShell and run this script again." -ForegroundColor Yellow
    exit 0
}

# Setup environment variables
Write-Host "🔧 Setting up environment variables..." -ForegroundColor Yellow
if (!(Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Created .env file from template. Please update with your credentials." -ForegroundColor Green
} else {
    Write-Host "ℹ️  .env file already exists" -ForegroundColor Blue
}

# Install root dependencies
Write-Host "📦 Installing root dependencies..." -ForegroundColor Yellow
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install root dependencies" -ForegroundColor Red
    exit 1
}

# Setup backend
Write-Host "🐍 Setting up backend..." -ForegroundColor Yellow
Set-Location "backend"
try {
    uv sync
    if ($LASTEXITCODE -ne 0) {
        throw "uv sync failed"
    }
    Write-Host "✅ Backend dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to setup backend: $_" -ForegroundColor Red
    exit 1
} finally {
    Set-Location ".."
}

# Setup frontend  
Write-Host "🎨 Setting up frontend..." -ForegroundColor Yellow
Set-Location "frontend"
try {
    npm install
    if ($LASTEXITCODE -ne 0) {
        throw "npm install failed"
    }
    Write-Host "✅ Frontend dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to setup frontend: $_" -ForegroundColor Red
    exit 1
} finally {
    Set-Location ".."
}

# Create development services info
Write-Host "🗄️  Setting up database..." -ForegroundColor Yellow
try {
    $dockerComposeExists = docker-compose --version 2>$null
    if ($dockerComposeExists) {
        Write-Host "Docker Compose found. You can run: docker-compose up -d" -ForegroundColor Blue
    } else {
        Write-Host "Using Supabase for database (recommended)" -ForegroundColor Blue
    }
} catch {
    Write-Host "Using Supabase for database (recommended)" -ForegroundColor Blue
}

Write-Host "✨ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🎯 Next steps:" -ForegroundColor Green
Write-Host "1. Update .env file with your Supabase and S3 credentials" -ForegroundColor Cyan
Write-Host "2. Run: docker-compose up -d" -ForegroundColor Cyan
Write-Host "3. Backend: cd backend; uv run uvicorn app.main:app --reload" -ForegroundColor Cyan
Write-Host "4. Frontend: cd frontend; npm run dev" -ForegroundColor Cyan
Write-Host ""
Write-Host "📖 Documentation: See README.md for detailed setup instructions" -ForegroundColor Blue
Write-Host "🌐 API Docs: http://localhost:8000/docs (when running)" -ForegroundColor Blue
Write-Host "🎨 Frontend: http://localhost:3000 (when running)" -ForegroundColor Blue