#!/bin/bash

# Resume Twin Platform - Development Setup Script
echo "🚀 Setting up Resume Twin Platform development environment..."

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed. Please install Node.js 18+"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.11+"
    exit 1
fi

# Install Astral UV
if ! command -v uv &> /dev/null; then
    echo "📦 Installing Astral UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "💡 Please restart your terminal or run: source ~/.cargo/env"
    exit 0
fi

# Setup environment variables
echo "🔧 Setting up environment variables..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file from template. Please update with your credentials."
else
    echo "ℹ️  .env file already exists"
fi

# Install root dependencies
echo "📦 Installing root dependencies..."
npm install

# Setup backend
echo "🐍 Setting up backend..."
cd backend
uv sync
cd ..

# Setup frontend  
echo "🎨 Setting up frontend..."
cd frontend
npm install
cd ..

# Create development database (if using local PostgreSQL)
echo "🗄️  Setting up database..."
if command -v psql &> /dev/null; then
    echo "PostgreSQL found. You can run: docker-compose up -d postgres"
else
    echo "PostgreSQL not found. Using Supabase for database."
fi

echo "✨ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Update .env file with your Supabase and S3 credentials"
echo "2. Run: docker-compose up -d"
echo "3. Backend: cd backend && uv run uvicorn app.main:app --reload"
echo "4. Frontend: cd frontend && npm run dev"
echo ""
echo "📖 Documentation: See README.md for detailed setup instructions"
echo "🌐 API Docs: http://localhost:8000/docs (when running)"
echo "🎨 Frontend: http://localhost:3000 (when running)"