"""Service layer modules for database operations."""

from .base import BaseService
from .profile_service import ProfileService
from .project_service import ProjectService
from .resume_service import ResumeService
from .template_service import TemplateService
from .file_service import FileService
from .supabase_service import SupabaseClient, supabase_client
from .s3_service import S3Service
from .latex_service import LaTeXService
from .ai_service import AIService, get_ai_service

# Alias for backward compatibility
LatexService = LaTeXService
SupabaseService = SupabaseClient
get_supabase_client = lambda: supabase_client

__all__ = [
    "BaseService",
    "ProfileService",
    "ProjectService",
    "ResumeService",
    "TemplateService",
    "FileService",
    "SupabaseClient",
    "SupabaseService",
    "supabase_client",
    "get_supabase_client",
    "S3Service",
    "LaTeXService",
    "LatexService",
    "AIService",
    "get_ai_service",
]