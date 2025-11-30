"""S3 storage service for file operations."""

import boto3
import os
from typing import Optional, Dict, Any, List
from uuid import UUID
from botocore.exceptions import ClientError, BotoCoreError
from datetime import datetime, timedelta
import mimetypes

from app.core.config import settings
from app.utils.logger import setup_logger
from app.models.files import FileValidationResult, FileManager

logger = setup_logger(__name__)


class S3Service:
    """Service for S3 file operations."""
    
    def __init__(self):
        """Initialize S3 client."""
        # Try Supabase Storage first, fallback to regular S3
        self.bucket_name = (
            settings.SUPABASE_STORAGE_BUCKET or
            settings.S3_BUCKET_NAME
        )
        self.region = settings.SUPABASE_STORAGE_REGION or settings.S3_REGION
        
        # Check for Supabase Storage configuration
        supabase_access_key = settings.SUPABASE_STORAGE_ACCESS_KEY
        supabase_secret_key = settings.SUPABASE_STORAGE_SECRET_KEY
        supabase_url = settings.SUPABASE_STORAGE_URL
        
        # Use Supabase Storage if available, otherwise fall back to regular S3
        if supabase_access_key and supabase_secret_key:
            # Supabase Storage (S3-compatible)
            logger.info("Using Supabase Storage for file operations")
            try:
                self.client = boto3.client(
                    's3',
                    aws_access_key_id=supabase_access_key,
                    aws_secret_access_key=supabase_secret_key,
                    region_name=self.region,
                    endpoint_url=supabase_url or f"{settings.SUPABASE_URL}/storage/v1/object"
                )
                logger.info("Supabase Storage client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase Storage client: {e}")
                self.client = None
        elif all([self.bucket_name, settings.S3_ACCESS_KEY, settings.S3_SECRET_KEY]):
            # Regular S3
            logger.info("Using regular S3 for file operations")
            try:
                self.client = boto3.client(
                    's3',
                    aws_access_key_id=settings.S3_ACCESS_KEY,
                    aws_secret_access_key=settings.S3_SECRET_KEY,
                    region_name=self.region,
                    endpoint_url=settings.S3_ENDPOINT_URL
                )
                logger.info("S3 client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize S3 client: {e}")
                self.client = None
        else:
            logger.warning("No storage credentials configured")
            self.client = None
    
    def upload_file(
        self, 
        file_content: bytes, 
        file_path: str, 
        content_type: str = None,
        metadata: Dict[str, str] = None
    ) -> bool:
        """Upload file to S3."""
        if not self.client:
            logger.error("S3 client not available")
            return False
        
        try:
            if not content_type:
                content_type, _ = mimetypes.guess_type(file_path)
                if not content_type:
                    content_type = 'application/octet-stream'
            
            extra_args = {
                'ContentType': content_type
            }
            
            if metadata:
                extra_args['Metadata'] = metadata
            
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=file_path,
                Body=file_content,
                **extra_args
            )
            
            logger.info(f"File uploaded successfully: {file_path}")
            return True
            
        except ClientError as e:
            logger.error(f"S3 upload error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during upload: {e}")
            return False
    
    def generate_presigned_upload_url(self, file_path: str, expires_in: int = 3600) -> Optional[str]:
        """Generate presigned URL for direct upload."""
        if not self.client:
            logger.error("S3 client not available")
            return None
        
        try:
            response = self.client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_path
                },
                ExpiresIn=expires_in
            )
            return response
            
        except ClientError as e:
            logger.error(f"Error generating presigned upload URL: {e}")
            return None
    
    def generate_presigned_download_url(self, file_path: str, expires_in: int = 3600) -> Optional[str]:
        """Generate presigned URL for download."""
        if not self.client:
            logger.error("S3 client not available")
            return None
        
        try:
            response = self.client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_path
                },
                ExpiresIn=expires_in
            )
            return response
            
        except ClientError as e:
            logger.error(f"Error generating presigned download URL: {e}")
            return None
    
    def download_file(self, file_path: str) -> Optional[bytes]:
        """Download file from S3."""
        if not self.client:
            logger.error("S3 client not available")
            return None
        
        try:
            response = self.client.get_object(
                Bucket=self.bucket_name,
                Key=file_path
            )
            return response['Body'].read()
            
        except ClientError as e:
            logger.error(f"Error downloading file {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during download: {e}")
            return None
    
    def delete_file(self, file_path: str) -> bool:
        """Delete file from S3."""
        if not self.client:
            logger.error("S3 client not available")
            return False
        
        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=file_path
            )
            logger.info(f"File deleted successfully: {file_path}")
            return True
            
        except ClientError as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            return False
    
    def file_exists(self, file_path: str) -> bool:
        """Check if file exists in S3."""
        if not self.client:
            logger.error("S3 client not available")
            return False
        
        try:
            self.client.head_object(
                Bucket=self.bucket_name,
                Key=file_path
            )
            return True
            
        except ClientError:
            return False
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get file metadata."""
        if not self.client:
            logger.error("S3 client not available")
            return None
        
        try:
            response = self.client.head_object(
                Bucket=self.bucket_name,
                Key=file_path
            )
            
            return {
                'size': response['ContentLength'],
                'last_modified': response['LastModified'],
                'content_type': response.get('ContentType'),
                'etag': response['ETag'],
                'metadata': response.get('Metadata', {})
            }
            
        except ClientError as e:
            logger.error(f"Error getting file info for {file_path}: {e}")
            return None
    
    def list_files(self, prefix: str = "", max_keys: int = 1000) -> List[Dict[str, Any]]:
        """List files in S3 bucket."""
        if not self.client:
            logger.error("S3 client not available")
            return []
        
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            files = []
            for obj in response.get('Contents', []):
                files.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'],
                    'etag': obj['ETag']
                })
            
            return files
            
        except ClientError as e:
            logger.error(f"Error listing files with prefix '{prefix}': {e}")
            return []
    
    def cleanup_old_files(self, prefix: str, days_old: int = 30) -> int:
        """Delete files older than specified days."""
        if not self.client:
            logger.error("S3 client not available")
            return 0
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        deleted_count = 0
        
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            for obj in response.get('Contents', []):
                if obj['LastModified'].replace(tzinfo=None) < cutoff_date:
                    if self.delete_file(obj['Key']):
                        deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} old files")
            return deleted_count
            
        except ClientError as e:
            logger.error(f"Error during cleanup: {e}")
            return 0


# Global S3 service instance
s3_service = S3Service()


def validate_and_upload_file(
    file_content: bytes,
    original_filename: str,
    file_category: str = 'other',
    user_id: UUID = None
) -> Dict[str, Any]:
    """Validate file and upload to S3."""
    # Prepare file data for validation
    file_data = {
        'original_filename': original_filename,
        'file_size': len(file_content),
        'mime_type': FileManager.get_mime_type(original_filename)
    }
    
    # Validate file
    validation_result = FileManager.validate_file(file_data)
    
    if not validation_result.is_valid:
        return {
            'success': False,
            'errors': validation_result.errors,
            'warnings': validation_result.warnings
        }
    
    # Generate file path
    if user_id:
        file_path = FileManager.generate_file_path(user_id, original_filename, file_category)
    else:
        import uuid
        from datetime import datetime as dt
        _, ext = original_filename.rsplit('.', 1)
        unique_filename = f"{uuid.uuid4()}.{ext}"
        timestamp = dt.now().strftime("%Y%m%d")
        file_path = f"uploads/{timestamp}/{unique_filename}"
    
    # Upload to S3
    from datetime import datetime
    metadata = {
        'original_filename': original_filename,
        'upload_timestamp': datetime.now().isoformat()
    }
    
    if user_id:
        metadata['user_id'] = str(user_id)
    
    success = s3_service.upload_file(
        file_content=file_content,
        file_path=file_path,
        content_type=validation_result.file_type,
        metadata=metadata
    )
    
    if success:
        return {
            'success': True,
            'file_path': file_path,
            'file_size': len(file_content),
            'mime_type': validation_result.file_type,
            'download_url': s3_service.generate_presigned_download_url(file_path),
            'validation_result': validation_result
        }
    else:
        return {
            'success': False,
            'errors': ['Failed to upload file to storage']
        }