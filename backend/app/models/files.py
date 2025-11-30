"""File upload and management models."""

from datetime import datetime, timezone
from typing import Optional, Dict
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
import mimetypes


class FileUploadBase(BaseModel):
    """Base file upload model."""
    original_filename: str = Field(..., min_length=1)
    file_size: Optional[int] = Field(None, ge=0)
    mime_type: Optional[str] = None
    file_category: Optional[str] = Field(None, pattern="^(avatar|certificate|project_media|resume_document|other)$")
    metadata: Dict = Field(default_factory=dict)


class FileUploadCreate(FileUploadBase):
    """File upload creation model."""
    pass


class FileUploadUpdate(BaseModel):
    """File upload update model."""
    original_filename: Optional[str] = None
    file_size: Optional[int] = Field(None, ge=0)
    mime_type: Optional[str] = None
    file_category: Optional[str] = Field(None, pattern="^(avatar|certificate|project_media|resume_document|other)$")
    upload_status: Optional[str] = Field(None, pattern="^(pending|processing|completed|failed)$")
    virus_scan_status: Optional[str] = Field(None, pattern="^(pending|scanning|clean|infected|error)$")
    processing_status: Optional[str] = Field(None, pattern="^(pending|processing|completed|failed)$")
    error_message: Optional[str] = None
    metadata: Optional[Dict] = None


class FileUpload(FileUploadBase):
    """File upload model from database."""
    id: UUID
    user_id: UUID
    file_path: str
    upload_status: str = "pending"
    virus_scan_status: str = "pending"
    processing_status: str = "pending"
    error_message: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

    @field_validator("mime_type", mode="before")
    @classmethod
    def validate_mime_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate and normalize MIME type."""
        if not v:
            return None
        return v.lower()


class FileUploadResponse(BaseModel):
    """File upload response model."""
    file_id: UUID
    upload_url: str
    file_path: str
    expires_at: Optional[datetime] = None


class FileUploadStatus(BaseModel):
    """File upload status model."""
    file_id: UUID
    upload_status: str
    virus_scan_status: str
    processing_status: str
    error_message: Optional[str] = None
    progress_percentage: int = Field(default=0, ge=0, le=100)


class FileDownloadResponse(BaseModel):
    """File download response model."""
    download_url: str
    expires_at: datetime
    content_type: str
    content_length: Optional[int] = None


class FileMetadata(BaseModel):
    """File metadata model."""
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[float] = None
    color_profile: Optional[str] = None
    exif_data: Optional[Dict] = None
    checksum: Optional[str] = None


class FileValidationResult(BaseModel):
    """File validation result model."""
    is_valid: bool
    errors: list = Field(default_factory=list)
    warnings: list = Field(default_factory=list)
    file_type: str
    is_safe: bool
    size_within_limits: bool


# File Management Utilities
class FileManager:
    """File management utility class."""
    
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_MIME_TYPES = {
        'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp',
        'application/pdf', 'text/plain',
        'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }
    
    ALLOWED_EXTENSIONS = {
        '.jpg', '.jpeg', '.png', '.gif', '.webp', '.pdf', '.txt', '.doc', '.docx'
    }
    
    @staticmethod
    def validate_file(file_data: dict) -> FileValidationResult:
        """Validate file data."""
        errors = []
        warnings = []
        
        # Check file size
        file_size = file_data.get('file_size', 0)
        if file_size > FileManager.MAX_FILE_SIZE:
            errors.append(f"File size ({file_size}) exceeds maximum limit ({FileManager.MAX_FILE_SIZE})")
        
        # Check MIME type
        mime_type = file_data.get('mime_type', '')
        if mime_type and mime_type not in FileManager.ALLOWED_MIME_TYPES:
            errors.append(f"MIME type '{mime_type}' is not allowed")
        
        # Check file extension
        filename = file_data.get('original_filename', '')
        if filename:
            import os
            _, ext = os.path.splitext(filename.lower())
            if ext not in FileManager.ALLOWED_EXTENSIONS:
                errors.append(f"File extension '{ext}' is not allowed")
        
        is_valid = len(errors) == 0
        is_safe = len([e for e in errors if 'virus' in e.lower()]) == 0
        
        return FileValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            file_type=mime_type or 'unknown',
            is_safe=is_safe,
            size_within_limits=file_size <= FileManager.MAX_FILE_SIZE
        )
    
    @staticmethod
    def generate_file_path(user_id: UUID, original_filename: str, category: str = 'other') -> str:
        """Generate file path for storage."""
        import uuid
        from datetime import datetime
        
        _, ext = original_filename.rsplit('.', 1)
        unique_filename = f"{uuid.uuid4()}.{ext}"
        
        timestamp = datetime.now().strftime("%Y%m%d")
        return f"uploads/{user_id}/{category}/{timestamp}/{unique_filename}"
    
    @staticmethod
    def get_mime_type(filename: str) -> str:
        """Get MIME type from filename."""
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type or 'application/octet-stream'
    
    @staticmethod
    def is_image_file(mime_type: str) -> bool:
        """Check if file is an image."""
        return mime_type and mime_type.startswith('image/')
    
    @staticmethod
    def is_document_file(mime_type: str) -> bool:
        """Check if file is a document."""
        return mime_type in {
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }


class FileStats(BaseModel):
    """File statistics model."""
    total_uploads: int = 0
    total_size_bytes: int = 0
    uploads_by_category: Dict = Field(default_factory=dict)
    uploads_by_mime_type: Dict = Field(default_factory=dict)
    average_file_size: float = 0.0
    most_recent_upload: Optional[datetime] = None
    failed_uploads: int = 0
    virus_detected: int = 0

    @property
    def total_size_mb(self) -> float:
        """Total size in MB."""
        return self.total_size_bytes / (1024 * 1024)
    
    @property
    def success_rate(self) -> float:
        """Upload success rate percentage."""
        if self.total_uploads == 0:
            return 0.0
        return ((self.total_uploads - self.failed_uploads) / self.total_uploads) * 100