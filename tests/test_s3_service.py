"""
Unit Tests for S3 Service.

Tests cover:
- S3 client initialization
- File upload
- File download
- Presigned URL generation
- File deletion
- File existence checking
- File listing
- Cleanup operations
- Error handling
"""

import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from datetime import datetime, timedelta
from botocore.exceptions import ClientError
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


# ============================================================================
# S3 Service Initialization Tests
# ============================================================================

class TestS3ServiceInit:
    """Tests for S3 service initialization."""
    
    def test_init_with_supabase_storage(self):
        """Should initialize with Supabase Storage when configured."""
        with patch('app.services.s3_service.settings') as mock_settings:
            mock_settings.SUPABASE_STORAGE_BUCKET = "test-bucket"
            mock_settings.SUPABASE_STORAGE_REGION = "us-east-1"
            mock_settings.SUPABASE_STORAGE_ACCESS_KEY = "access-key"
            mock_settings.SUPABASE_STORAGE_SECRET_KEY = "secret-key"
            mock_settings.SUPABASE_STORAGE_URL = "https://storage.supabase.co"
            mock_settings.SUPABASE_URL = "https://project.supabase.co"
            mock_settings.S3_BUCKET_NAME = None
            mock_settings.S3_ACCESS_KEY = None
            mock_settings.S3_SECRET_KEY = None
            mock_settings.S3_REGION = "us-east-1"
            mock_settings.S3_ENDPOINT_URL = None
            
            with patch('boto3.client') as mock_boto:
                from importlib import reload
                import app.services.s3_service as s3_module
                reload(s3_module)
                
                mock_boto.assert_called()
    
    def test_init_with_regular_s3(self):
        """Should initialize with regular S3 when configured."""
        with patch('app.services.s3_service.settings') as mock_settings:
            mock_settings.SUPABASE_STORAGE_BUCKET = None
            mock_settings.SUPABASE_STORAGE_REGION = None
            mock_settings.SUPABASE_STORAGE_ACCESS_KEY = None
            mock_settings.SUPABASE_STORAGE_SECRET_KEY = None
            mock_settings.SUPABASE_STORAGE_URL = None
            mock_settings.S3_BUCKET_NAME = "test-bucket"
            mock_settings.S3_ACCESS_KEY = "access-key"
            mock_settings.S3_SECRET_KEY = "secret-key"
            mock_settings.S3_REGION = "us-east-1"
            mock_settings.S3_ENDPOINT_URL = None
            
            with patch('boto3.client') as mock_boto:
                from app.services.s3_service import S3Service
                service = S3Service()


# ============================================================================
# File Upload Tests
# ============================================================================

class TestFileUpload:
    """Tests for file upload functionality."""
    
    @pytest.fixture
    def mock_s3_service(self):
        """Create mock S3 service."""
        with patch('app.services.s3_service.settings') as mock_settings:
            mock_settings.SUPABASE_STORAGE_BUCKET = "test-bucket"
            mock_settings.SUPABASE_STORAGE_REGION = "us-east-1"
            mock_settings.SUPABASE_STORAGE_ACCESS_KEY = "key"
            mock_settings.SUPABASE_STORAGE_SECRET_KEY = "secret"
            mock_settings.SUPABASE_STORAGE_URL = None
            mock_settings.SUPABASE_URL = "https://test.supabase.co"
            mock_settings.S3_BUCKET_NAME = "test-bucket"
            mock_settings.S3_ACCESS_KEY = "key"
            mock_settings.S3_SECRET_KEY = "secret"
            mock_settings.S3_REGION = "us-east-1"
            mock_settings.S3_ENDPOINT_URL = None
            
            from app.services.s3_service import S3Service
            service = S3Service()
            service.client = MagicMock()
            service.bucket_name = "test-bucket"
            return service
    
    def test_upload_file_success(self, mock_s3_service):
        """Should successfully upload file."""
        file_content = b"Test file content"
        file_path = "uploads/test.pdf"
        
        mock_s3_service.client.put_object.return_value = {}
        
        result = mock_s3_service.upload_file(file_content, file_path, "application/pdf")
        
        assert result is True
        mock_s3_service.client.put_object.assert_called_once()
    
    def test_upload_file_with_metadata(self, mock_s3_service):
        """Should upload file with metadata."""
        file_content = b"Test content"
        file_path = "uploads/test.pdf"
        metadata = {"user_id": "123", "original_name": "resume.pdf"}
        
        mock_s3_service.client.put_object.return_value = {}
        
        result = mock_s3_service.upload_file(
            file_content, 
            file_path, 
            "application/pdf",
            metadata=metadata
        )
        
        assert result is True
        call_args = mock_s3_service.client.put_object.call_args
        assert call_args.kwargs.get("Metadata") == metadata
    
    def test_upload_file_auto_content_type(self, mock_s3_service):
        """Should auto-detect content type."""
        file_content = b"Test content"
        file_path = "uploads/test.pdf"
        
        mock_s3_service.client.put_object.return_value = {}
        
        result = mock_s3_service.upload_file(file_content, file_path)
        
        assert result is True
    
    def test_upload_file_client_error(self, mock_s3_service):
        """Should handle client errors."""
        mock_s3_service.client.put_object.side_effect = ClientError(
            {"Error": {"Code": "500", "Message": "Internal Error"}},
            "PutObject"
        )
        
        result = mock_s3_service.upload_file(b"content", "test.pdf")
        
        assert result is False
    
    def test_upload_file_no_client(self):
        """Should return False when client not available."""
        with patch('app.services.s3_service.settings') as mock_settings:
            mock_settings.SUPABASE_STORAGE_ACCESS_KEY = None
            mock_settings.SUPABASE_STORAGE_SECRET_KEY = None
            mock_settings.S3_BUCKET_NAME = None
            mock_settings.S3_ACCESS_KEY = None
            mock_settings.S3_SECRET_KEY = None
            
            from app.services.s3_service import S3Service
            service = S3Service()
            service.client = None
            
            result = service.upload_file(b"content", "test.pdf")
            
            assert result is False


# ============================================================================
# File Download Tests
# ============================================================================

class TestFileDownload:
    """Tests for file download functionality."""
    
    @pytest.fixture
    def mock_s3_service(self):
        """Create mock S3 service."""
        from app.services.s3_service import S3Service
        with patch.object(S3Service, '__init__', lambda x: None):
            service = S3Service()
            service.client = MagicMock()
            service.bucket_name = "test-bucket"
            return service
    
    def test_download_file_success(self, mock_s3_service):
        """Should successfully download file."""
        file_content = b"Downloaded content"
        
        mock_body = MagicMock()
        mock_body.read.return_value = file_content
        mock_s3_service.client.get_object.return_value = {"Body": mock_body}
        
        result = mock_s3_service.download_file("uploads/test.pdf")
        
        assert result == file_content
    
    def test_download_file_not_found(self, mock_s3_service):
        """Should return None when file not found."""
        mock_s3_service.client.get_object.side_effect = ClientError(
            {"Error": {"Code": "NoSuchKey", "Message": "Not found"}},
            "GetObject"
        )
        
        result = mock_s3_service.download_file("nonexistent.pdf")
        
        assert result is None


# ============================================================================
# Presigned URL Tests
# ============================================================================

class TestPresignedUrls:
    """Tests for presigned URL generation."""
    
    @pytest.fixture
    def mock_s3_service(self):
        """Create mock S3 service."""
        from app.services.s3_service import S3Service
        with patch.object(S3Service, '__init__', lambda x: None):
            service = S3Service()
            service.client = MagicMock()
            service.bucket_name = "test-bucket"
            return service
    
    def test_generate_presigned_upload_url(self, mock_s3_service):
        """Should generate presigned upload URL."""
        expected_url = "https://s3.amazonaws.com/bucket/file?signed=upload"
        mock_s3_service.client.generate_presigned_url.return_value = expected_url
        
        result = mock_s3_service.generate_presigned_upload_url("uploads/test.pdf")
        
        assert result == expected_url
        mock_s3_service.client.generate_presigned_url.assert_called_once_with(
            'put_object',
            Params={'Bucket': 'test-bucket', 'Key': 'uploads/test.pdf'},
            ExpiresIn=3600
        )
    
    def test_generate_presigned_download_url(self, mock_s3_service):
        """Should generate presigned download URL."""
        expected_url = "https://s3.amazonaws.com/bucket/file?signed=download"
        mock_s3_service.client.generate_presigned_url.return_value = expected_url
        
        result = mock_s3_service.generate_presigned_download_url("uploads/test.pdf")
        
        assert result == expected_url
    
    def test_generate_presigned_url_custom_expiry(self, mock_s3_service):
        """Should use custom expiry time."""
        mock_s3_service.client.generate_presigned_url.return_value = "https://url"
        
        mock_s3_service.generate_presigned_download_url("test.pdf", expires_in=7200)
        
        call_args = mock_s3_service.client.generate_presigned_url.call_args
        assert call_args.kwargs.get('ExpiresIn') == 7200
    
    def test_generate_presigned_url_error(self, mock_s3_service):
        """Should return None on error."""
        mock_s3_service.client.generate_presigned_url.side_effect = ClientError(
            {"Error": {"Code": "500", "Message": "Error"}},
            "GeneratePresignedUrl"
        )
        
        result = mock_s3_service.generate_presigned_download_url("test.pdf")
        
        assert result is None


# ============================================================================
# File Deletion Tests
# ============================================================================

class TestFileDeletion:
    """Tests for file deletion."""
    
    @pytest.fixture
    def mock_s3_service(self):
        """Create mock S3 service."""
        from app.services.s3_service import S3Service
        with patch.object(S3Service, '__init__', lambda x: None):
            service = S3Service()
            service.client = MagicMock()
            service.bucket_name = "test-bucket"
            return service
    
    def test_delete_file_success(self, mock_s3_service):
        """Should successfully delete file."""
        mock_s3_service.client.delete_object.return_value = {}
        
        result = mock_s3_service.delete_file("uploads/test.pdf")
        
        assert result is True
        mock_s3_service.client.delete_object.assert_called_once_with(
            Bucket="test-bucket",
            Key="uploads/test.pdf"
        )
    
    def test_delete_file_error(self, mock_s3_service):
        """Should return False on error."""
        mock_s3_service.client.delete_object.side_effect = ClientError(
            {"Error": {"Code": "500", "Message": "Error"}},
            "DeleteObject"
        )
        
        result = mock_s3_service.delete_file("test.pdf")
        
        assert result is False


# ============================================================================
# File Existence Tests
# ============================================================================

class TestFileExistence:
    """Tests for file existence checking."""
    
    @pytest.fixture
    def mock_s3_service(self):
        """Create mock S3 service."""
        from app.services.s3_service import S3Service
        with patch.object(S3Service, '__init__', lambda x: None):
            service = S3Service()
            service.client = MagicMock()
            service.bucket_name = "test-bucket"
            return service
    
    def test_file_exists_true(self, mock_s3_service):
        """Should return True when file exists."""
        mock_s3_service.client.head_object.return_value = {"ContentLength": 1024}
        
        result = mock_s3_service.file_exists("uploads/test.pdf")
        
        assert result is True
    
    def test_file_exists_false(self, mock_s3_service):
        """Should return False when file doesn't exist."""
        mock_s3_service.client.head_object.side_effect = ClientError(
            {"Error": {"Code": "404", "Message": "Not Found"}},
            "HeadObject"
        )
        
        result = mock_s3_service.file_exists("nonexistent.pdf")
        
        assert result is False


# ============================================================================
# File Info Tests
# ============================================================================

class TestFileInfo:
    """Tests for file info retrieval."""
    
    @pytest.fixture
    def mock_s3_service(self):
        """Create mock S3 service."""
        from app.services.s3_service import S3Service
        with patch.object(S3Service, '__init__', lambda x: None):
            service = S3Service()
            service.client = MagicMock()
            service.bucket_name = "test-bucket"
            return service
    
    def test_get_file_info_success(self, mock_s3_service):
        """Should return file metadata."""
        mock_s3_service.client.head_object.return_value = {
            "ContentLength": 1024,
            "LastModified": datetime.utcnow(),
            "ContentType": "application/pdf",
            "ETag": '"abc123"',
            "Metadata": {"user_id": "123"}
        }
        
        result = mock_s3_service.get_file_info("uploads/test.pdf")
        
        assert result is not None
        assert result["size"] == 1024
        assert result["content_type"] == "application/pdf"
    
    def test_get_file_info_not_found(self, mock_s3_service):
        """Should return None when file not found."""
        mock_s3_service.client.head_object.side_effect = ClientError(
            {"Error": {"Code": "404", "Message": "Not Found"}},
            "HeadObject"
        )
        
        result = mock_s3_service.get_file_info("nonexistent.pdf")
        
        assert result is None


# ============================================================================
# File Listing Tests
# ============================================================================

class TestFileListing:
    """Tests for file listing."""
    
    @pytest.fixture
    def mock_s3_service(self):
        """Create mock S3 service."""
        from app.services.s3_service import S3Service
        with patch.object(S3Service, '__init__', lambda x: None):
            service = S3Service()
            service.client = MagicMock()
            service.bucket_name = "test-bucket"
            return service
    
    def test_list_files_success(self, mock_s3_service):
        """Should return list of files."""
        mock_s3_service.client.list_objects_v2.return_value = {
            "Contents": [
                {
                    "Key": "uploads/file1.pdf",
                    "Size": 1024,
                    "LastModified": datetime.utcnow(),
                    "ETag": '"abc"'
                },
                {
                    "Key": "uploads/file2.pdf",
                    "Size": 2048,
                    "LastModified": datetime.utcnow(),
                    "ETag": '"def"'
                }
            ]
        }
        
        result = mock_s3_service.list_files("uploads/")
        
        assert len(result) == 2
        assert result[0]["key"] == "uploads/file1.pdf"
    
    def test_list_files_empty(self, mock_s3_service):
        """Should return empty list when no files."""
        mock_s3_service.client.list_objects_v2.return_value = {}
        
        result = mock_s3_service.list_files("uploads/")
        
        assert result == []


# ============================================================================
# Cleanup Tests
# ============================================================================

class TestCleanup:
    """Tests for cleanup operations."""
    
    @pytest.fixture
    def mock_s3_service(self):
        """Create mock S3 service."""
        from app.services.s3_service import S3Service
        with patch.object(S3Service, '__init__', lambda x: None):
            service = S3Service()
            service.client = MagicMock()
            service.bucket_name = "test-bucket"
            return service
    
    def test_cleanup_old_files(self, mock_s3_service):
        """Should delete files older than specified days."""
        old_date = datetime.now() - timedelta(days=60)
        recent_date = datetime.now() - timedelta(days=10)
        
        mock_s3_service.client.list_objects_v2.return_value = {
            "Contents": [
                {"Key": "old_file.pdf", "LastModified": old_date},
                {"Key": "recent_file.pdf", "LastModified": recent_date}
            ]
        }
        mock_s3_service.client.delete_object.return_value = {}
        
        # Mock delete_file method
        mock_s3_service.delete_file = MagicMock(return_value=True)
        
        result = mock_s3_service.cleanup_old_files("uploads/", days_old=30)
        
        assert result == 1  # Only old file deleted


# ============================================================================
# Validate and Upload Tests
# ============================================================================

class TestValidateAndUpload:
    """Tests for validate_and_upload_file function."""
    
    def test_validate_and_upload_success(self):
        """Should validate and upload file successfully."""
        with patch('app.services.s3_service.FileManager') as mock_fm:
            with patch('app.services.s3_service.s3_service') as mock_s3:
                mock_fm.get_mime_type.return_value = "application/pdf"
                mock_fm.validate_file.return_value = MagicMock(
                    is_valid=True,
                    file_type="application/pdf",
                    errors=[],
                    warnings=[]
                )
                mock_fm.generate_file_path.return_value = "uploads/user/file.pdf"
                mock_s3.upload_file.return_value = True
                mock_s3.generate_presigned_download_url.return_value = "https://url"
                
                from app.services.s3_service import validate_and_upload_file
                
                result = validate_and_upload_file(
                    b"PDF content",
                    "resume.pdf",
                    "resume",
                    uuid4()
                )
                
                assert result["success"] is True
                assert "file_path" in result
    
    def test_validate_and_upload_validation_failure(self):
        """Should return errors when validation fails."""
        with patch('app.services.s3_service.FileManager') as mock_fm:
            mock_fm.get_mime_type.return_value = "application/x-msdownload"
            mock_fm.validate_file.return_value = MagicMock(
                is_valid=False,
                errors=["File type not allowed"],
                warnings=[]
            )
            
            from app.services.s3_service import validate_and_upload_file
            
            result = validate_and_upload_file(
                b"EXE content",
                "malware.exe",
                "other"
            )
            
            assert result["success"] is False
            assert "File type not allowed" in result["errors"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
