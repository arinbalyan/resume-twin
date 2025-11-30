"""File upload and management endpoints."""

from fastapi import APIRouter, HTTPException, Depends, Query, File, UploadFile, Form
from typing import List, Optional
from uuid import UUID
import io
from ...services.file_service import FileService
from ...models.files import FileUpload, FileUploadResponse, FileDownloadResponse, FileStats
from ...utils.logger import setup_logger

logger = setup_logger(__name__)
file_service = FileService()

router = APIRouter()


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    file_category: str = Form("other"),
    user_id: Optional[str] = Query(None, description="User ID (temporary for development)")
):
    """Upload a file with automatic validation and storage."""
    try:
        # Read file content
        content = await file.read()
        
        # Validate file size
        if len(content) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=413, detail="File too large (max 10MB)")
        
        # Generate user ID (temporary for development)
        if not user_id:
            user_id = "00000000-0000-0000-0000-000000000000"
        
        # Upload and register file
        result = file_service.upload_and_register_file(
            user_id=UUID(user_id),
            file_content=content,
            original_filename=file.filename,
            file_category=file_category
        )
        
        if result['success']:
            return FileUploadResponse(
                file_id=UUID(result['file_id']),
                upload_url=result['download_url'],  # Same as download for now
                file_path=result['file_path'],
                expires_at=result['expires_at']
            )
        else:
            raise HTTPException(status_code=400, detail=result.get('errors', ['Upload failed']))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/", response_model=List[FileUpload])
async def get_user_files(
    user_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    category: Optional[str] = Query(None)
):
    """Get user's uploaded files with pagination and filtering."""
    try:
        # Generate user ID (temporary for development)
        if not user_id:
            user_id = "00000000-0000-0000-0000-000000000000"
        
        files = file_service.get_user_files(UUID(user_id), limit, offset)
        
        # Filter by category if specified
        if category:
            files = [f for f in files if f.file_category == category]
        
        return files
        
    except Exception as e:
        logger.error(f"Error getting user files: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{file_id}", response_model=FileUpload)
async def get_file(file_id: str, user_id: Optional[str] = Query(None)):
    """Get specific file information."""
    try:
        # Generate user ID (temporary for development)
        if not user_id:
            user_id = "00000000-0000-0000-0000-000000000000"
        
        file_record = file_service.get_file_by_id(UUID(file_id), UUID(user_id))
        if file_record:
            return file_record
        else:
            raise HTTPException(status_code=404, detail="File not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file {file_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{file_id}/download", response_model=FileDownloadResponse)
async def download_file(file_id: str, user_id: Optional[str] = Query(None)):
    """Generate download URL for file."""
    try:
        # Generate user ID (temporary for development)
        if not user_id:
            user_id = "00000000-0000-0000-0000-000000000000"
        
        download_url = file_service.generate_download_url(UUID(file_id), UUID(user_id))
        if download_url:
            # Get file info for response
            file_record = file_service.get_file_by_id(UUID(file_id), UUID(user_id))
            if file_record:
                return FileDownloadResponse(
                    download_url=download_url,
                    expires_at=file_record.expires_at,
                    content_type=file_record.mime_type or 'application/octet-stream',
                    content_length=file_record.file_size
                )
        
        raise HTTPException(status_code=404, detail="File not found or expired")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating download URL for file {file_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{file_id}")
async def delete_file(file_id: str, user_id: Optional[str] = Query(None)):
    """Delete file from storage and database."""
    try:
        # Generate user ID (temporary for development)
        if not user_id:
            user_id = "00000000-0000-0000-0000-000000000000"
        
        success = file_service.delete_file(UUID(file_id), UUID(user_id))
        if success:
            return {"message": "File deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="File not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file {file_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{file_id}/status", response_model=dict)
async def get_file_status(file_id: str, user_id: Optional[str] = Query(None)):
    """Get file processing status."""
    try:
        # Generate user ID (temporary for development)
        if not user_id:
            user_id = "00000000-0000-0000-0000-000000000000"
        
        file_record = file_service.get_file_by_id(UUID(file_id), UUID(user_id))
        if file_record:
            return {
                "file_id": file_id,
                "upload_status": file_record.upload_status,
                "virus_scan_status": file_record.virus_scan_status,
                "processing_status": file_record.processing_status,
                "error_message": file_record.error_message
            }
        else:
            raise HTTPException(status_code=404, detail="File not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file status for {file_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/stats/user", response_model=FileStats)
async def get_user_file_stats(user_id: Optional[str] = Query(None)):
    """Get file statistics for user."""
    try:
        # Generate user ID (temporary for development)
        if not user_id:
            user_id = "00000000-0000-0000-0000-000000000000"
        
        stats = file_service.get_file_stats(UUID(user_id))
        return stats
        
    except Exception as e:
        logger.error(f"Error getting file stats for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/cleanup/expired")
async def cleanup_expired_files():
    """Clean up expired files (admin endpoint)."""
    try:
        # In production, this would require admin authentication
        deleted_count = file_service.cleanup_expired_files()
        return {"message": f"Cleaned up {deleted_count} expired files"}
        
    except Exception as e:
        logger.error(f"Error during expired files cleanup: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/cleanup/validate")
async def validate_all_files():
    """Validate all uploaded files (admin endpoint)."""
    try:
        # This would implement file validation logic
        # For now, return a placeholder response
        return {"message": "File validation completed", "validated": 0, "errors": 0}
        
    except Exception as e:
        logger.error(f"Error during file validation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")