"""PDF Storage Service - Handles storing and retrieving generated PDFs from Supabase Storage."""

import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
import time

from app.core.config import settings
from app.utils.logger import setup_logger
from app.services.s3_service import s3_service
from app.services.supabase_service import supabase_client

logger = setup_logger(__name__)


class PDFStorageService:
    """
    Service for storing and retrieving generated PDFs.
    
    Features:
    - Store PDFs in Supabase Storage (S3-compatible)
    - Track metadata in database
    - Generate secure download URLs
    - User-based access control
    - Download analytics
    """
    
    # Storage path format: resumes/{user_id}/{pdf_id}.pdf
    STORAGE_PREFIX = "resumes"
    
    def __init__(self):
        """Initialize PDF storage service."""
        self.bucket_name = settings.SUPABASE_STORAGE_BUCKET or "resumes"
    
    def _generate_storage_path(self, user_id: UUID, pdf_id: UUID) -> str:
        """Generate storage path for a PDF file."""
        return f"{self.STORAGE_PREFIX}/{str(user_id)}/{str(pdf_id)}.pdf"
    
    def _compute_content_hash(self, content: bytes) -> str:
        """Compute SHA-256 hash of PDF content for deduplication."""
        return hashlib.sha256(content).hexdigest()
    
    async def store_pdf(
        self,
        pdf_content: bytes,
        user_id: UUID,
        file_name: str,
        template_name: str = None,
        template_type: str = "html",
        generation_method: str = "pdfshift",
        generation_time_ms: int = None,
        resume_version_id: UUID = None,
        expires_in_days: int = None
    ) -> Dict[str, Any]:
        """
        Store a generated PDF in Supabase Storage and record metadata in database.
        
        Args:
            pdf_content: The PDF file content as bytes
            user_id: The user who owns this PDF
            file_name: Display name for the PDF
            template_name: Name of template used
            template_type: "html" or "latex"
            generation_method: How the PDF was generated (pdfshift, browserless, etc.)
            generation_time_ms: Generation time in milliseconds
            resume_version_id: Optional link to a resume version
            expires_in_days: Optional expiration in days (None = never expires)
        
        Returns:
            Dict with success status and PDF metadata
        """
        try:
            # Generate unique PDF ID
            pdf_id = uuid4()
            
            # Generate storage path
            storage_path = self._generate_storage_path(user_id, pdf_id)
            
            # Compute content hash
            content_hash = self._compute_content_hash(pdf_content)
            
            # Calculate file size
            file_size = len(pdf_content)
            
            # Calculate expiration if specified
            expires_at = None
            if expires_in_days:
                expires_at = datetime.now() + timedelta(days=expires_in_days)
            
            # Upload to S3/Supabase Storage
            start_time = time.time()
            upload_success = s3_service.upload_file(
                file_content=pdf_content,
                file_path=storage_path,
                content_type="application/pdf",
                metadata={
                    "user_id": str(user_id),
                    "original_name": file_name,
                    "template": template_name or "unknown",
                    "method": generation_method
                }
            )
            upload_time = int((time.time() - start_time) * 1000)
            
            if not upload_success:
                logger.error(f"Failed to upload PDF to storage: {storage_path}")
                return {
                    "success": False,
                    "error": "Failed to upload PDF to storage"
                }
            
            logger.info(f"PDF uploaded to storage: {storage_path} ({file_size} bytes, {upload_time}ms)")
            
            # Record metadata in database
            pdf_record = {
                "id": str(pdf_id),
                "user_id": str(user_id),
                "resume_version_id": str(resume_version_id) if resume_version_id else None,
                "file_name": file_name,
                "storage_path": storage_path,
                "file_size": file_size,
                "mime_type": "application/pdf",
                "template_name": template_name,
                "template_type": template_type,
                "generation_method": generation_method,
                "generation_time_ms": generation_time_ms,
                "generation_status": "completed",
                "content_hash": content_hash,
                "is_public": False,
                "expires_at": expires_at.isoformat() if expires_at else None
            }
            
            # Insert into database
            if supabase_client:
                try:
                    result = supabase_client.table("generated_pdfs").insert(pdf_record).execute()
                    logger.info(f"PDF metadata stored in database: {pdf_id}")
                except Exception as db_error:
                    logger.warning(f"Failed to store PDF metadata in database: {db_error}")
                    # Still return success since file is uploaded
            
            return {
                "success": True,
                "pdf_id": str(pdf_id),
                "storage_path": storage_path,
                "file_name": file_name,
                "file_size": file_size,
                "content_hash": content_hash,
                "expires_at": expires_at.isoformat() if expires_at else None
            }
            
        except Exception as e:
            logger.error(f"Error storing PDF: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_download_url(
        self,
        pdf_id: UUID,
        user_id: UUID,
        expires_in: int = 3600
    ) -> Optional[str]:
        """
        Generate a presigned download URL for a PDF.
        
        Args:
            pdf_id: The PDF ID
            user_id: The requesting user's ID (must own the PDF)
            expires_in: URL expiration in seconds (default 1 hour)
        
        Returns:
            Presigned URL or None if not authorized
        """
        try:
            # First, verify the user owns this PDF
            if supabase_client:
                result = supabase_client.table("generated_pdfs").select(
                    "id, user_id, storage_path, file_name"
                ).eq("id", str(pdf_id)).execute()
                
                if not result.data:
                    logger.warning(f"PDF not found: {pdf_id}")
                    return None
                
                pdf_record = result.data[0]
                
                # Check ownership
                if pdf_record["user_id"] != str(user_id):
                    logger.warning(f"User {user_id} attempted to access PDF owned by {pdf_record['user_id']}")
                    return None
                
                storage_path = pdf_record["storage_path"]
            else:
                # If no database, construct path from user_id and pdf_id
                storage_path = self._generate_storage_path(user_id, pdf_id)
            
            # Generate presigned URL
            url = s3_service.generate_presigned_download_url(storage_path, expires_in)
            
            if url:
                # Log the download
                await self._log_download(pdf_id, user_id, "presigned_url")
            
            return url
            
        except Exception as e:
            logger.error(f"Error generating download URL: {e}")
            return None
    
    async def download_pdf(
        self,
        pdf_id: UUID,
        user_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """
        Download a PDF directly.
        
        Args:
            pdf_id: The PDF ID
            user_id: The requesting user's ID (must own the PDF)
        
        Returns:
            Dict with file content and metadata, or None if not authorized
        """
        try:
            # Verify ownership and get metadata
            if supabase_client:
                result = supabase_client.table("generated_pdfs").select("*").eq(
                    "id", str(pdf_id)
                ).execute()
                
                if not result.data:
                    logger.warning(f"PDF not found: {pdf_id}")
                    return None
                
                pdf_record = result.data[0]
                
                # Check ownership
                if pdf_record["user_id"] != str(user_id):
                    logger.warning(f"User {user_id} attempted to download PDF owned by {pdf_record['user_id']}")
                    return None
                
                storage_path = pdf_record["storage_path"]
                file_name = pdf_record["file_name"]
            else:
                storage_path = self._generate_storage_path(user_id, pdf_id)
                file_name = f"resume_{pdf_id}.pdf"
            
            # Download from storage
            content = s3_service.download_file(storage_path)
            
            if not content:
                logger.error(f"Failed to download PDF from storage: {storage_path}")
                return None
            
            # Log the download
            await self._log_download(pdf_id, user_id, "direct")
            
            return {
                "content": content,
                "file_name": file_name,
                "content_type": "application/pdf",
                "file_size": len(content)
            }
            
        except Exception as e:
            logger.error(f"Error downloading PDF: {e}")
            return None
    
    async def get_public_download_url(
        self,
        public_token: UUID,
        expires_in: int = 3600
    ) -> Optional[Dict[str, Any]]:
        """
        Get download URL for a public PDF using its public token.
        
        Args:
            public_token: The public sharing token
            expires_in: URL expiration in seconds
        
        Returns:
            Dict with URL and file info, or None if not found/not public
        """
        try:
            if not supabase_client:
                return None
            
            result = supabase_client.table("generated_pdfs").select(
                "id, storage_path, file_name, is_public"
            ).eq("public_token", str(public_token)).eq("is_public", True).execute()
            
            if not result.data:
                logger.warning(f"Public PDF not found with token: {public_token}")
                return None
            
            pdf_record = result.data[0]
            
            url = s3_service.generate_presigned_download_url(
                pdf_record["storage_path"], 
                expires_in
            )
            
            if url:
                await self._log_download(UUID(pdf_record["id"]), None, "public_link")
            
            return {
                "url": url,
                "file_name": pdf_record["file_name"]
            }
            
        except Exception as e:
            logger.error(f"Error getting public download URL: {e}")
            return None
    
    async def list_user_pdfs(
        self,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List all PDFs owned by a user.
        
        Args:
            user_id: The user's ID
            limit: Maximum number of results
            offset: Pagination offset
        
        Returns:
            List of PDF metadata
        """
        try:
            if not supabase_client:
                return []
            
            result = supabase_client.table("generated_pdfs").select(
                "id, file_name, file_size, template_name, generation_method, "
                "download_count, is_public, created_at"
            ).eq("user_id", str(user_id)).order(
                "created_at", desc=True
            ).range(offset, offset + limit - 1).execute()
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"Error listing user PDFs: {e}")
            return []
    
    async def delete_pdf(
        self,
        pdf_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Delete a PDF and its storage.
        
        Args:
            pdf_id: The PDF ID
            user_id: The user's ID (must own the PDF)
        
        Returns:
            True if deleted, False otherwise
        """
        try:
            # Get PDF record and verify ownership
            if supabase_client:
                result = supabase_client.table("generated_pdfs").select(
                    "id, user_id, storage_path"
                ).eq("id", str(pdf_id)).execute()
                
                if not result.data:
                    return False
                
                pdf_record = result.data[0]
                
                if pdf_record["user_id"] != str(user_id):
                    logger.warning(f"User {user_id} attempted to delete PDF owned by {pdf_record['user_id']}")
                    return False
                
                storage_path = pdf_record["storage_path"]
            else:
                storage_path = self._generate_storage_path(user_id, pdf_id)
            
            # Delete from storage
            storage_deleted = s3_service.delete_file(storage_path)
            
            # Delete from database
            if supabase_client:
                supabase_client.table("generated_pdfs").delete().eq(
                    "id", str(pdf_id)
                ).execute()
            
            logger.info(f"PDF deleted: {pdf_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting PDF: {e}")
            return False
    
    async def toggle_public(
        self,
        pdf_id: UUID,
        user_id: UUID,
        is_public: bool
    ) -> Optional[Dict[str, Any]]:
        """
        Toggle public sharing for a PDF.
        
        Args:
            pdf_id: The PDF ID
            user_id: The user's ID (must own the PDF)
            is_public: Whether to make the PDF public
        
        Returns:
            Updated PDF info with public_token if made public
        """
        try:
            if not supabase_client:
                return None
            
            # Verify ownership
            result = supabase_client.table("generated_pdfs").select(
                "id, user_id, public_token"
            ).eq("id", str(pdf_id)).execute()
            
            if not result.data:
                return None
            
            if result.data[0]["user_id"] != str(user_id):
                return None
            
            # Update public status
            update_result = supabase_client.table("generated_pdfs").update({
                "is_public": is_public
            }).eq("id", str(pdf_id)).execute()
            
            if update_result.data:
                return {
                    "is_public": is_public,
                    "public_token": result.data[0]["public_token"] if is_public else None
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error toggling public status: {e}")
            return None
    
    async def _log_download(
        self,
        pdf_id: UUID,
        user_id: Optional[UUID],
        download_type: str
    ):
        """Log a PDF download event."""
        try:
            if not supabase_client:
                return
            
            log_record = {
                "pdf_id": str(pdf_id),
                "user_id": str(user_id) if user_id else None,
                "download_type": download_type
            }
            
            supabase_client.table("pdf_download_logs").insert(log_record).execute()
            
            # Increment download count
            supabase_client.rpc("increment_pdf_download_count", {"pdf_uuid": str(pdf_id)}).execute()
            
        except Exception as e:
            logger.warning(f"Failed to log download: {e}")
    
    async def get_user_storage_stats(self, user_id: UUID) -> Dict[str, Any]:
        """
        Get storage statistics for a user.
        
        Args:
            user_id: The user's ID
        
        Returns:
            Dict with storage stats
        """
        try:
            if not supabase_client:
                return {"total_pdfs": 0, "total_storage_bytes": 0}
            
            result = supabase_client.table("generated_pdfs").select(
                "file_size"
            ).eq("user_id", str(user_id)).execute()
            
            if not result.data:
                return {"total_pdfs": 0, "total_storage_bytes": 0}
            
            total_pdfs = len(result.data)
            total_bytes = sum(record["file_size"] for record in result.data)
            
            return {
                "total_pdfs": total_pdfs,
                "total_storage_bytes": total_bytes,
                "total_storage_mb": round(total_bytes / (1024 * 1024), 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting storage stats: {e}")
            return {"total_pdfs": 0, "total_storage_bytes": 0}


# Global service instance
pdf_storage_service = PDFStorageService()
