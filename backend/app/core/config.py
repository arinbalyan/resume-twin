"""Application configuration settings."""

from pathlib import Path
from typing import List, Optional
from pydantic import AnyHttpUrl, EmailStr, HttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic.networks import PostgresDsn

# Get the project root directory (parent of backend/)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Project Information
    PROJECT_NAME: str = "Resume Twin API"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "Portfolio & Resume Generation Platform API"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None
    DATABASE_URL: Optional[PostgresDsn] = None
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # S3 Storage
    S3_BUCKET_NAME: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_REGION: str = "ap-south-1"
    S3_ENDPOINT_URL: Optional[str] = None
    
    # Supabase Storage (S3-compatible)
    SUPABASE_STORAGE_ACCESS_KEY: Optional[str] = None
    SUPABASE_STORAGE_SECRET_KEY: Optional[str] = None
    SUPABASE_STORAGE_BUCKET: Optional[str] = "portfolio-files"
    SUPABASE_STORAGE_REGION: str = "us-east-1"
    SUPABASE_STORAGE_URL: Optional[str] = None
    
    # OpenRouter AI Configuration
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_MODEL: str = "openai/gpt-oss-20b:free"
    AI_MODEL: Optional[str] = None  # Defaults to OPENROUTER_MODEL if not set
    
    # AI Service Configuration
    AI_TIMEOUT_SECONDS: int = 30
    AI_MAX_RETRIES: int = 3
    AI_CIRCUIT_BREAKER_THRESHOLD: int = 5
    AI_CIRCUIT_BREAKER_TIMEOUT: int = 60
    AI_MAX_TOKENS: int = 4000
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["pdf", "jpg", "jpeg", "png", "doc", "docx"]
    
    # PDF Generation Configuration
    PDF_GENERATION_METHOD: str = "html"  # Options: "latex", "html", "overleaf"
    LATEX_COMPILATION_TIMEOUT: int = 60
    LATEX_COMPILE_SERVER_URL: Optional[str] = None
    TEMPLATES_DIR: str = str(PROJECT_ROOT / "templates")  # Directory containing templates
    
    # HTML-to-PDF Configuration (for weasyprint)
    HTML_TO_PDF_ENABLED: bool = True
    
    # Overleaf API Configuration
    OVERLEAF_API_URL: Optional[str] = None
    OVERLEAF_API_TOKEN: Optional[str] = None
    OVERLEAF_TEMPLATE_ID: Optional[str] = None
    
    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[EmailStr] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_TLS: bool = True
    
    # AI Services
    OPENAI_API_KEY: Optional[str] = None
    AI_OPTIMIZATION_ENABLED: bool = True
    
    # ============== FREE API INTEGRATIONS ==============
    
    # GitHub API (FREE - 5000 req/hr with token, 60/hr without)
    # Get token at: https://github.com/settings/tokens (no scopes needed for public repos)
    GITHUB_TOKEN: Optional[str] = None
    
    # Hunter.io Email Verification (FREE - 50 verifications/month)
    # Get key at: https://hunter.io/api
    HUNTER_API_KEY: Optional[str] = None
    
    # Abstract API Email Validation (FREE - 100 requests/month)
    # Get key at: https://www.abstractapi.com/email-validation-api
    ABSTRACT_EMAIL_API_KEY: Optional[str] = None
    
    # Clearbit Company Data (FREE for logos)
    # Get key at: https://clearbit.com/logo
    CLEARBIT_API_KEY: Optional[str] = None
    
    # IPInfo Location Detection (FREE - 50,000 requests/month)
    # Get key at: https://ipinfo.io/signup
    IPINFO_TOKEN: Optional[str] = None
    
    # Unsplash Images (FREE - 50 requests/hour)
    # Get keys at: https://unsplash.com/developers
    UNSPLASH_ACCESS_KEY: Optional[str] = None
    
    # PDFShift HTML-to-PDF API (FREE - 50 conversions/month)
    # Get key at: https://pdfshift.io/
    PDFSHIFT_API_KEY: Optional[str] = None
    
    # ============== END FREE API INTEGRATIONS ==============
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Monitoring
    SENTRY_DSN: Optional[HttpUrl] = None
    LOG_LEVEL: str = "INFO"
    
    # Deployment
    RAILWAY_TOKEN: Optional[str] = None
    VERCEL_TOKEN: Optional[str] = None
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: List[str] | str) -> List[str]:
        """Validate and assemble CORS origins."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        else:
            raise ValueError(v)
    
    @field_validator("ALLOWED_FILE_TYPES", mode="before")
    @classmethod
    def validate_file_types(cls, v: List[str] | str) -> List[str]:
        """Validate allowed file types."""
        if isinstance(v, str):
            return [item.strip().lower() for item in v.split(",")]
        return [item.lower() for item in v]
    
    @field_validator("MAX_FILE_SIZE")
    @classmethod
    def validate_max_file_size(cls, v: int) -> int:
        """Validate maximum file size is reasonable."""
        if v < 1024:  # Less than 1KB
            raise ValueError("MAX_FILE_SIZE must be at least 1024 bytes")
        if v > 100 * 1024 * 1024:  # More than 100MB
            raise ValueError("MAX_FILE_SIZE must be less than 100MB")
        return v
    
    @field_validator("SENTRY_DSN", mode="before")
    @classmethod
    def sentry_dsn_validation(cls, v: Optional[str]) -> Optional[HttpUrl]:
        """Validate Sentry DSN format."""
        if v:
            try:
                return HttpUrl(v)
            except Exception:
                raise ValueError("Invalid Sentry DSN format")
        return v
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        env_file_encoding="utf-8",
        extra="allow"
    )


# Global settings instance
settings = Settings()