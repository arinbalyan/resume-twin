"""
Unit Tests for File Service.

Tests cover:
- File upload and registration
- File validation
- File retrieval and download URL generation
- File deletion
- File statistics calculation
"""

import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from datetime import datetime, timedelta, timezone
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


def make_sample_file_record():
    """Create sample file record."""
    return {
        "id": uuid4(),
        "user_id": uuid4(),
        "original_filename": "resume.pdf",
        "file_size": 102400,
        "mime_type": "application/pdf",
        "file_category": "resume_document",
        "file_path": f"uploads/{uuid4()}/resume.pdf",
        "upload_status": "completed",
        "virus_scan_status": "clean",
        "processing_status": "completed",
        "error_message": None,
        "metadata": {},
        "expires_at": datetime.now(timezone.utc) + timedelta(days=365),
        "created_at": datetime.now(timezone.utc)
    }


@pytest.fixture
def sample_file_record():
    """Fixture for sample file record."""
    return make_sample_file_record()


@pytest.fixture
def mock_file_service():
    """Create mock file service."""
    with patch('app.services.file_service.BaseService.__init__', return_value=None):
        from app.services.file_service import FileService
        service = FileService()
        service.table_name = "file_uploads"
        service.client = MagicMock()
        return service


class TestFileServiceCRUD:
    """Tests for File Service CRUD operations."""
    
    def test_get_user_files_empty(self, mock_file_service):
        """Should return empty list when user has no files."""
        user_id = uuid4()
        mock_file_service.filter = MagicMock(return_value=[])
        
        result = mock_file_service.get_user_files(user_id)
        
        assert result == []
        mock_file_service.filter.assert_called_once()
    
    def test_get_user_files_with_data(self, mock_file_service, sample_file_record):
        """Should return list of files for user."""
        user_id = uuid4()
        sample_file_record["user_id"] = user_id
        mock_file_service.filter = MagicMock(return_value=[sample_file_record])
        
        result = mock_file_service.get_user_files(user_id)
        
        assert len(result) == 1
        assert result[0].original_filename == "resume.pdf"
    
    def test_get_file_by_id_found(self, mock_file_service, sample_file_record):
        """Should return file when found."""
        file_id = uuid4()
        mock_file_service.get_by_id = MagicMock(return_value=sample_file_record)
        
        result = mock_file_service.get_file_by_id(file_id)
        
        assert result is not None
        assert result.original_filename == "resume.pdf"
    
    def test_get_file_by_id_not_found(self, mock_file_service):
        """Should return None when file not found."""
        file_id = uuid4()
        mock_file_service.get_by_id = MagicMock(return_value=None)
        
        result = mock_file_service.get_file_by_id(file_id)
        
        assert result is None
    
    def test_get_file_by_id_with_user_check_authorized(self, mock_file_service, sample_file_record):
        """Should return file when user is authorized."""
        file_id = uuid4()
        user_id = uuid4()
        # The actual code compares result['user_id'] (string) with str(user_id)
        sample_file_record["user_id"] = str(user_id)
        mock_file_service.get_by_id = MagicMock(return_value=sample_file_record)
        
        result = mock_file_service.get_file_by_id(file_id, user_id)
        
        assert result is not None
    
    def test_get_file_by_id_with_user_check_unauthorized(self, mock_file_service, sample_file_record):
        """Should return None when user is not authorized."""
        file_id = uuid4()
        user_id = uuid4()
        other_user_id = uuid4()
        sample_file_record["user_id"] = other_user_id
        mock_file_service.get_by_id = MagicMock(return_value=sample_file_record)
        
        result = mock_file_service.get_file_by_id(file_id, user_id)
        
        assert result is None


class TestFileUpload:
    """Tests for file upload functionality."""
    
    def test_upload_and_register_success(self, mock_file_service):
        """Should successfully upload and register file."""
        user_id = uuid4()
        file_content = b"PDF content here"
        
        with patch('app.services.file_service.validate_and_upload_file') as mock_validate:
            mock_validate.return_value = {
                'success': True,
                'file_path': f'uploads/{user_id}/test.pdf',
                'file_size': len(file_content),
                'mime_type': 'application/pdf',
                'download_url': 'https://example.com/download',
                'validation_result': MagicMock(is_valid=True)
            }
            
            mock_file_service.create_file_record = MagicMock(return_value=MagicMock(
                id=uuid4(),
                expires_at=datetime.now(timezone.utc) + timedelta(days=365)
            ))
            
            result = mock_file_service.upload_and_register_file(
                user_id=user_id,
                file_content=file_content,
                original_filename="test.pdf",
                file_category="resume_document"
            )
            
            assert result['success'] is True
            assert 'file_id' in result
    
    def test_upload_validation_failure(self, mock_file_service):
        """Should return error when validation fails."""
        user_id = uuid4()
        
        with patch('app.services.file_service.validate_and_upload_file') as mock_validate:
            mock_validate.return_value = {
                'success': False,
                'errors': ['File type not allowed']
            }
            
            result = mock_file_service.upload_and_register_file(
                user_id=user_id,
                file_content=b"invalid content",
                original_filename="malware.exe",
                file_category="other"
            )
            
            assert result['success'] is False
            assert 'File type not allowed' in result['errors']


class TestDownloadUrlGeneration:
    """Tests for download URL generation."""
    
    def test_generate_download_url_success(self, mock_file_service, sample_file_record):
        """Should generate valid download URL."""
        file_id = uuid4()
        
        # The actual code uses datetime.utcnow() (naive) for comparison, so expires_at must be naive too
        mock_file_service.get_file_by_id = MagicMock(return_value=MagicMock(
            file_path=sample_file_record['file_path'],
            expires_at=datetime.utcnow() + timedelta(days=30)  # Use naive datetime to match source
        ))
        
        with patch('app.services.file_service.s3_service') as mock_s3:
            mock_s3.generate_presigned_download_url.return_value = "https://signed-url.com/file"
            
            result = mock_file_service.generate_download_url(file_id)
            
            assert result == "https://signed-url.com/file"
    
    def test_generate_download_url_expired_file(self, mock_file_service, sample_file_record):
        """Should return None for expired files."""
        file_id = uuid4()
        
        mock_file_service.get_file_by_id = MagicMock(return_value=MagicMock(
            file_path=sample_file_record['file_path'],
            expires_at=datetime.now(timezone.utc) - timedelta(days=1)
        ))
        
        result = mock_file_service.generate_download_url(file_id)
        
        assert result is None
    
    def test_generate_download_url_file_not_found(self, mock_file_service):
        """Should return None when file not found."""
        file_id = uuid4()
        mock_file_service.get_file_by_id = MagicMock(return_value=None)
        
        result = mock_file_service.generate_download_url(file_id)
        
        assert result is None


class TestFileDeletion:
    """Tests for file deletion."""
    
    def test_delete_file_success(self, mock_file_service, sample_file_record):
        """Should successfully delete file from S3 and database."""
        file_id = uuid4()
        
        mock_file_service.get_file_by_id = MagicMock(return_value=MagicMock(
            file_path=sample_file_record['file_path']
        ))
        mock_file_service.delete = MagicMock(return_value=True)
        
        with patch('app.services.file_service.s3_service') as mock_s3:
            mock_s3.delete_file.return_value = True
            
            result = mock_file_service.delete_file(file_id)
            
            assert result is True
            mock_s3.delete_file.assert_called_once()
            mock_file_service.delete.assert_called_once()
    
    def test_delete_file_not_found(self, mock_file_service):
        """Should return False when file not found."""
        file_id = uuid4()
        mock_file_service.get_file_by_id = MagicMock(return_value=None)
        
        result = mock_file_service.delete_file(file_id)
        
        assert result is False


class TestFileModels:
    """Tests for file-related Pydantic models."""
    
    def test_file_upload_create(self):
        """Should create file upload with required fields."""
        from app.models.files import FileUploadCreate
        
        upload = FileUploadCreate(original_filename="test.pdf")
        
        assert upload.original_filename == "test.pdf"
        assert upload.file_size is None
    
    def test_file_upload_create_full(self):
        """Should create file upload with all fields."""
        from app.models.files import FileUploadCreate
        
        upload = FileUploadCreate(
            original_filename="test.pdf",
            file_size=1024,
            mime_type="application/pdf",
            file_category="resume_document"
        )
        
        assert upload.file_size == 1024
        assert upload.mime_type == "application/pdf"
    
    def test_file_validation_result(self):
        """Should create validation result."""
        from app.models.files import FileValidationResult
        
        result = FileValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            file_type="application/pdf",
            is_safe=True,
            size_within_limits=True
        )
        
        assert result.is_valid is True
        assert result.is_safe is True
    
    def test_file_stats_defaults(self):
        """Should have correct default values."""
        from app.models.files import FileStats
        
        stats = FileStats()
        
        assert stats.total_uploads == 0
        assert stats.total_size_bytes == 0
        assert stats.failed_uploads == 0
    
    def test_file_stats_properties(self):
        """Should calculate properties correctly."""
        from app.models.files import FileStats
        
        stats = FileStats(
            total_uploads=10,
            total_size_bytes=10 * 1024 * 1024,
            failed_uploads=2
        )
        
        assert stats.total_size_mb == 10.0
        assert stats.success_rate == 80.0


class TestFileManager:
    """Tests for FileManager utility class."""
    
    def test_validate_file_valid(self):
        """Should return valid result for valid file."""
        from app.models.files import FileManager
        
        file_data = {
            'original_filename': 'test.pdf',
            'file_size': 1024,
            'mime_type': 'application/pdf'
        }
        
        result = FileManager.validate_file(file_data)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_file_size_exceeded(self):
        """Should return error for oversized file."""
        from app.models.files import FileManager
        
        file_data = {
            'original_filename': 'large.pdf',
            'file_size': 20 * 1024 * 1024,
            'mime_type': 'application/pdf'
        }
        
        result = FileManager.validate_file(file_data)
        
        assert result.is_valid is False
        assert any('exceeds maximum' in e for e in result.errors)
    
    def test_validate_file_invalid_type(self):
        """Should return error for invalid file type."""
        from app.models.files import FileManager
        
        file_data = {
            'original_filename': 'script.exe',
            'file_size': 1024,
            'mime_type': 'application/x-msdownload'
        }
        
        result = FileManager.validate_file(file_data)
        
        assert result.is_valid is False
    
    def test_get_mime_type(self):
        """Should return correct MIME type."""
        from app.models.files import FileManager
        
        assert FileManager.get_mime_type('test.pdf') == 'application/pdf'
        assert FileManager.get_mime_type('image.png') == 'image/png'
        assert FileManager.get_mime_type('unknown.xyz') == 'application/octet-stream'
    
    def test_is_image_file(self):
        """Should correctly identify image files."""
        from app.models.files import FileManager
        
        assert FileManager.is_image_file('image/png') is True
        assert FileManager.is_image_file('image/jpeg') is True
        assert FileManager.is_image_file('application/pdf') is False
    
    def test_is_document_file(self):
        """Should correctly identify document files."""
        from app.models.files import FileManager
        
        assert FileManager.is_document_file('application/pdf') is True
        assert FileManager.is_document_file('application/msword') is True
        assert FileManager.is_document_file('image/png') is False
    
    def test_generate_file_path(self):
        """Should generate valid file path."""
        from app.models.files import FileManager
        
        user_id = uuid4()
        path = FileManager.generate_file_path(user_id, 'test.pdf', 'resume')
        
        assert str(user_id) in path
        assert 'resume' in path
        assert path.endswith('.pdf')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
