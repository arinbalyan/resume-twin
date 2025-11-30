"""File service for file operations with S3 integration."""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from app.services.base import BaseService
from app.models.files import FileUpload, FileUploadCreate, FileStats
from app.services.s3_service import s3_service, validate_and_upload_file
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class FileService(BaseService):
    """Service for file-related operations with S3 integration."""
    
    def __init__(self):
        """Initialize file service."""
        super().__init__("file_uploads")
    
    def create_file_record(self, user_id: UUID, file_data: FileUploadCreate, file_path: str) -> Optional[FileUpload]:
        """Create file upload record in database."""
        file_dict = file_data.dict()
        file_dict.update({
            "user_id": str(user_id),
            "file_path": file_path,
            "upload_status": "completed",
            "virus_scan_status": "clean",  # TODO: Implement virus scanning
            "processing_status": "completed",
            "expires_at": datetime.utcnow() + timedelta(days=365)  # 1 year expiration
        })
        
        try:
            result = self.create(file_dict)
            if result:
                return FileUpload(**result)
            return None
        except Exception as e:
            logger.error(f"Error creating file record: {e}")
            return None
    
    def upload_and_register_file(
        self, 
        user_id: UUID,
        file_content: bytes, 
        original_filename: str, 
        file_category: str = 'other'
    ) -> Dict[str, Any]:
        """Upload file to S3 and register in database."""
        try:
            # Validate and upload to S3
            upload_result = validate_and_upload_file(
                file_content=file_content,
                original_filename=original_filename,
                file_category=file_category,
                user_id=user_id
            )
            
            if not upload_result['success']:
                return upload_result
            
            # Create database record
            file_data = FileUploadCreate(
                original_filename=original_filename,
                file_size=upload_result['file_size'],
                mime_type=upload_result['mime_type'],
                file_category=file_category
            )
            
            file_record = self.create_file_record(
                user_id=user_id,
                file_data=file_data,
                file_path=upload_result['file_path']
            )
            
            if file_record:
                return {
                    'success': True,
                    'file_id': file_record.id,
                    'file_path': upload_result['file_path'],
                    'download_url': upload_result['download_url'],
                    'file_size': upload_result['file_size'],
                    'mime_type': upload_result['mime_type'],
                    'expires_at': file_record.expires_at,
                    'validation_result': upload_result['validation_result']
                }
            else:
                # Cleanup uploaded file if database record creation fails
                s3_service.delete_file(upload_result['file_path'])
                return {
                    'success': False,
                    'errors': ['Failed to create file record']
                }
                
        except Exception as e:
            logger.error(f"Error in upload_and_register_file: {e}")
            return {
                'success': False,
                'errors': [f'Upload failed: {str(e)}']
            }
    
    def get_user_files(self, user_id: UUID, limit: int = 50, offset: int = 0) -> List[FileUpload]:
        """Get files for a specific user."""
        try:
            results = self.filter({"user_id": str(user_id)}, limit, offset)
            return [FileUpload(**file_record) for file_record in results]
        except Exception as e:
            logger.error(f"Error getting files for user {user_id}: {e}")
            return []
    
    def get_file_by_id(self, file_id: UUID, user_id: UUID = None) -> Optional[FileUpload]:
        """Get file by ID, optionally checking user ownership."""
        try:
            result = self.get_by_id(file_id)
            if result:
                # Check user ownership if user_id provided
                if user_id and result['user_id'] != str(user_id):
                    return None
                return FileUpload(**result)
            return None
        except Exception as e:
            logger.error(f"Error getting file {file_id}: {e}")
            return None
    
    def generate_download_url(self, file_id: UUID, user_id: UUID = None) -> Optional[str]:
        """Generate signed download URL for file."""
        try:
            file_record = self.get_file_by_id(file_id, user_id)
            if not file_record:
                return None
            
            # Check if file has expired
            if file_record.expires_at and file_record.expires_at < datetime.utcnow():
                logger.warning(f"File {file_id} has expired")
                return None
            
            # Generate signed URL
            signed_url = s3_service.generate_presigned_download_url(
                file_record.file_path,
                expires_in=3600  # 1 hour
            )
            
            return signed_url
            
        except Exception as e:
            logger.error(f"Error generating download URL for file {file_id}: {e}")
            return None
    
    def delete_file(self, file_id: UUID, user_id: UUID = None) -> bool:
        """Delete file from both S3 and database."""
        try:
            file_record = self.get_file_by_id(file_id, user_id)
            if not file_record:
                return False
            
            # Delete from S3
            s3_deleted = s3_service.delete_file(file_record.file_path)
            
            # Delete from database
            db_deleted = self.delete(file_id)
            
            if s3_deleted and db_deleted:
                logger.info(f"File {file_id} deleted successfully from both S3 and database")
                return True
            else:
                logger.warning(f"Partial deletion of file {file_id}: S3={s3_deleted}, DB={db_deleted}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting file {file_id}: {e}")
            return False
    
    def update_file_status(self, file_id: UUID, status_updates: Dict[str, Any]) -> bool:
        """Update file status (virus scan, processing, etc.)."""
        try:
            return bool(self.update(file_id, status_updates))
        except Exception as e:
            logger.error(f"Error updating file status for {file_id}: {e}")
            return False
    
    def get_file_stats(self, user_id: UUID) -> FileStats:
        """Get file statistics for a user."""
        try:
            files = self.get_user_files(user_id, limit=10000)  # Get all files for stats
            
            total_uploads = len(files)
            total_size = sum(file.file_size or 0 for file in files)
            
            # Calculate category distribution
            uploads_by_category = {}
            for file in files:
                category = file.file_category or 'other'
                uploads_by_category[category] = uploads_by_category.get(category, 0) + 1
            
            # Calculate MIME type distribution
            uploads_by_mime = {}
            for file in files:
                mime_type = file.mime_type or 'unknown'
                uploads_by_mime[mime_type] = uploads_by_mime.get(mime_type, 0) + 1
            
            # Count failed uploads
            failed_uploads = sum(1 for file in files if file.upload_status == 'failed')
            
            # Get most recent upload
            most_recent = None
            if files:
                most_recent = max(files, key=lambda x: x.created_at).created_at
            
            return FileStats(
                total_uploads=total_uploads,
                total_size_bytes=total_size,
                uploads_by_category=uploads_by_category,
                uploads_by_mime_type=uploads_by_mime,
                average_file_size=total_size / total_uploads if total_uploads > 0 else 0.0,
                most_recent_upload=most_recent,
                failed_uploads=failed_uploads,
                virus_detected=0  # TODO: Implement virus detection tracking
            )
            
        except Exception as e:
            logger.error(f"Error calculating file stats for user {user_id}: {e}")
            return FileStats()
    
    def cleanup_expired_files(self, days_old: int = 30) -> int:
        """Clean up expired files."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            # Get expired files
            expired_files = self.filter({"expires_at": {"lt": cutoff_date.isoformat()}})
            
            deleted_count = 0
            for file_record in expired_files:
                file_id = UUID(file_record['id'])
                if self.delete_file(file_id):
                    deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} expired files")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error during expired files cleanup: {e}")
            return 0
    
    def cleanup_s3_old_files(self, user_id: UUID, days_old: int = 30) -> int:
        """Clean up old files from S3 storage."""
        try:
            prefix = f"uploads/{user_id}/"
            return s3_service.cleanup_old_files(prefix, days_old)
        except Exception as e:
            logger.error(f"Error during S3 cleanup for user {user_id}: {e}")
            return 0