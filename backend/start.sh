#!/bin/bash
# =====================================================
# Render Start Script
# =====================================================
# Optimized for Render free tier (512MB RAM)
# This script is used when deploying via render.yaml
# =====================================================

set -e

echo "🚀 Starting Resume Twin API on Render..."

# Environment info
echo "📦 Environment: ${ENVIRONMENT:-production}"
echo "🐍 Python: $(python --version)"
echo "📍 Port: ${PORT:-8000}"

# Memory optimization
export MALLOC_ARENA_MAX=2
export PYTHONMALLOC=malloc

# Start uvicorn with optimized settings for free tier
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "${PORT:-8000}" \
    --workers 1 \
    --limit-concurrency 50 \
    --timeout-keep-alive 120 \
    --log-level info
