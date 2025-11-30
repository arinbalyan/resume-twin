"""
Custom exception hierarchy for Resume Twin application.

This module defines all custom exceptions used throughout the application,
following NASA-level error handling standards with comprehensive error codes,
messages, and context information.

Author: Resume Twin Development Team
Version: 1.0.0
"""

from typing import Any, Dict, Optional
from enum import Enum


class ErrorCode(str, Enum):
    """
    Enumeration of all error codes in the application.
    
    This provides a structured way to identify and categorize errors,
    enabling better error tracking, monitoring, and user feedback.
    """
    
    # General errors (1000-1999)
    INTERNAL_SERVER_ERROR = "ERR_1000"
    VALIDATION_ERROR = "ERR_1001"
    NOT_FOUND = "ERR_1002"
    UNAUTHORIZED = "ERR_1003"
    FORBIDDEN = "ERR_1004"
    CONFLICT = "ERR_1005"
    
    # Database errors (2000-2999)
    DATABASE_CONNECTION_ERROR = "ERR_2000"
    DATABASE_QUERY_ERROR = "ERR_2001"
    DATABASE_TRANSACTION_ERROR = "ERR_2002"
    DATABASE_CONSTRAINT_VIOLATION = "ERR_2003"
    
    # Authentication errors (3000-3999)
    AUTH_INVALID_CREDENTIALS = "ERR_3000"
    AUTH_TOKEN_EXPIRED = "ERR_3001"
    AUTH_TOKEN_INVALID = "ERR_3002"
    AUTH_SESSION_EXPIRED = "ERR_3003"
    
    # AI Service errors (4000-4999)
    AI_SERVICE_UNAVAILABLE = "ERR_4000"
    AI_API_ERROR = "ERR_4001"
    AI_RATE_LIMIT_EXCEEDED = "ERR_4002"
    AI_INVALID_RESPONSE = "ERR_4003"
    AI_TIMEOUT = "ERR_4004"
    AI_QUOTA_EXCEEDED = "ERR_4005"
    
    # File Service errors (5000-5999)
    FILE_NOT_FOUND = "ERR_5000"
    FILE_UPLOAD_ERROR = "ERR_5001"
    FILE_SIZE_EXCEEDED = "ERR_5002"
    FILE_TYPE_INVALID = "ERR_5003"
    FILE_VIRUS_DETECTED = "ERR_5004"
    
    # LaTeX Service errors (6000-6999)
    LATEX_COMPILATION_ERROR = "ERR_6000"
    LATEX_TEMPLATE_NOT_FOUND = "ERR_6001"
    LATEX_SYNTAX_ERROR = "ERR_6002"
    
    # Job Analysis errors (7000-7999)
    JOB_PARSING_ERROR = "ERR_7000"
    JOB_DESCRIPTION_INVALID = "ERR_7001"
    JOB_REQUIREMENTS_EMPTY = "ERR_7002"
    
    # Resume Optimization errors (8000-8999)
    RESUME_OPTIMIZATION_ERROR = "ERR_8000"
    RESUME_PROFILE_INCOMPLETE = "ERR_8001"
    RESUME_GENERATION_ERROR = "ERR_8002"


class ResumeTwinException(Exception):
    """
    Base exception class for all Resume Twin exceptions.
    
    This class provides a structured way to handle errors with:
    - Error codes for programmatic error handling
    - Human-readable error messages
    - Additional context data
    - HTTP status codes for API responses
    
    Attributes:
        error_code: Unique error code from ErrorCode enum
        message: Human-readable error message
        details: Additional context about the error
        status_code: HTTP status code for API responses
    """
    
    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500
    ) -> None:
        """
        Initialize the exception with error details.
        
        Args:
            error_code: Unique error code from ErrorCode enum
            message: Human-readable error message
            details: Additional context about the error
            status_code: HTTP status code for API responses (default: 500)
        """
        self.error_code: ErrorCode = error_code
        self.message: str = message
        self.details: Dict[str, Any] = details or {}
        self.status_code: int = status_code
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary for API responses.
        
        Returns:
            Dictionary containing error information
        """
        return {
            "error_code": self.error_code.value,
            "message": self.message,
            "details": self.details
        }


# Database Exceptions

class DatabaseException(ResumeTwinException):
    """Base exception for all database-related errors."""
    
    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(error_code, message, details, status_code=500)


class DatabaseConnectionError(DatabaseException):
    """Raised when database connection fails."""
    
    def __init__(self, message: str = "Failed to connect to database", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(ErrorCode.DATABASE_CONNECTION_ERROR, message, details)


class DatabaseQueryError(DatabaseException):
    """Raised when database query execution fails."""
    
    def __init__(self, message: str = "Database query failed", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(ErrorCode.DATABASE_QUERY_ERROR, message, details)


# Authentication Exceptions

class AuthenticationException(ResumeTwinException):
    """Base exception for all authentication-related errors."""
    
    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(error_code, message, details, status_code=401)


class InvalidCredentialsError(AuthenticationException):
    """Raised when authentication credentials are invalid."""
    
    def __init__(self, message: str = "Invalid credentials", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(ErrorCode.AUTH_INVALID_CREDENTIALS, message, details)


class TokenExpiredError(AuthenticationException):
    """Raised when authentication token has expired."""
    
    def __init__(self, message: str = "Token has expired", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(ErrorCode.AUTH_TOKEN_EXPIRED, message, details)


# AI Service Exceptions

class AIServiceException(ResumeTwinException):
    """Base exception for all AI service-related errors."""
    
    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500
    ) -> None:
        super().__init__(error_code, message, details, status_code)


class AIServiceUnavailableError(AIServiceException):
    """Raised when AI service is unavailable or unreachable."""
    
    def __init__(self, message: str = "AI service is unavailable", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(ErrorCode.AI_SERVICE_UNAVAILABLE, message, details, status_code=503)


class AIAPIError(AIServiceException):
    """Raised when AI API returns an error response."""
    
    def __init__(self, message: str = "AI API request failed", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(ErrorCode.AI_API_ERROR, message, details)


class AIRateLimitError(AIServiceException):
    """Raised when AI API rate limit is exceeded."""
    
    def __init__(self, message: str = "AI API rate limit exceeded", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(ErrorCode.AI_RATE_LIMIT_EXCEEDED, message, details, status_code=429)


class AITimeoutError(AIServiceException):
    """Raised when AI API request times out."""
    
    def __init__(self, message: str = "AI API request timed out", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(ErrorCode.AI_TIMEOUT, message, details, status_code=504)


class AIInvalidResponseError(AIServiceException):
    """Raised when AI API returns invalid or malformed response."""
    
    def __init__(self, message: str = "AI API returned invalid response", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(ErrorCode.AI_INVALID_RESPONSE, message, details)


# Job Analysis Exceptions

class JobAnalysisException(ResumeTwinException):
    """Base exception for job analysis errors."""
    
    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(error_code, message, details, status_code=400)


class JobParsingError(JobAnalysisException):
    """Raised when job description parsing fails."""
    
    def __init__(self, message: str = "Failed to parse job description", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(ErrorCode.JOB_PARSING_ERROR, message, details)


class JobDescriptionInvalidError(JobAnalysisException):
    """Raised when job description is invalid or empty."""
    
    def __init__(self, message: str = "Job description is invalid", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(ErrorCode.JOB_DESCRIPTION_INVALID, message, details)


# Resume Optimization Exceptions

class ResumeOptimizationException(ResumeTwinException):
    """Base exception for resume optimization errors."""
    
    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(error_code, message, details, status_code=400)


class ResumeProfileIncompleteError(ResumeOptimizationException):
    """Raised when user profile is incomplete for resume generation."""
    
    def __init__(self, message: str = "User profile is incomplete", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(ErrorCode.RESUME_PROFILE_INCOMPLETE, message, details)


class ResumeGenerationError(ResumeOptimizationException):
    """Raised when resume generation fails."""
    
    def __init__(self, message: str = "Resume generation failed", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(ErrorCode.RESUME_GENERATION_ERROR, message, details)


# File Service Exceptions

class FileServiceException(ResumeTwinException):
    """Base exception for file service errors."""
    
    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 400
    ) -> None:
        super().__init__(error_code, message, details, status_code)


class FileNotFoundError(FileServiceException):
    """Raised when requested file is not found."""
    
    def __init__(self, message: str = "File not found", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(ErrorCode.FILE_NOT_FOUND, message, details, status_code=404)


class FileSizeExceededError(FileServiceException):
    """Raised when uploaded file exceeds size limit."""
    
    def __init__(self, message: str = "File size exceeds limit", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(ErrorCode.FILE_SIZE_EXCEEDED, message, details)


class FileTypeInvalidError(FileServiceException):
    """Raised when uploaded file type is not allowed."""
    
    def __init__(self, message: str = "File type not allowed", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(ErrorCode.FILE_TYPE_INVALID, message, details)


# LaTeX Service Exceptions

class LaTeXServiceException(ResumeTwinException):
    """Base exception for LaTeX service errors."""
    
    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(error_code, message, details, status_code=500)


class LaTeXCompilationError(LaTeXServiceException):
    """Raised when LaTeX compilation fails."""
    
    def __init__(self, message: str = "LaTeX compilation failed", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(ErrorCode.LATEX_COMPILATION_ERROR, message, details)


class LaTeXTemplateNotFoundError(LaTeXServiceException):
    """Raised when LaTeX template is not found."""
    
    def __init__(self, message: str = "LaTeX template not found", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(ErrorCode.LATEX_TEMPLATE_NOT_FOUND, message, details)