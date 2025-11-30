"""Health check endpoints."""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "resume-twin-api"
    }


@router.get("/detailed")
async def detailed_health_check():
    """Detailed health check with system information."""
    import sys
    import os
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "resume-twin-api",
        "version": "0.1.0",
        "python_version": sys.version,
        "environment": os.getenv("ENVIRONMENT", "development"),
        "uptime": "N/A"  # Would implement uptime tracking in production
    }