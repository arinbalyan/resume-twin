"""Database connection and client setup."""

from typing import Optional
from supabase import create_client, Client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize Supabase client
supabase_client: Optional[Client] = None

if settings.SUPABASE_URL and settings.SUPABASE_KEY:
    try:
        supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        logger.info("Supabase client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        supabase_client = None
else:
    logger.warning("Supabase URL or key not configured. Database functionality will be limited.")


def get_supabase_client() -> Optional[Client]:
    """Get the Supabase client instance."""
    return supabase_client


def test_connection() -> bool:
    """Test database connection."""
    if not supabase_client:
        return False
    
    try:
        response = supabase_client.table("profiles").select("count").execute()
        logger.info("Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


# Database health check function
async def database_health_check() -> dict:
    """Perform database health check."""
    try:
        if test_connection():
            return {"status": "healthy", "database": "connected"}
        else:
            return {"status": "unhealthy", "database": "disconnected"}
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {"status": "error", "database": str(e)}