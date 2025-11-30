"""Supabase client service for database operations."""

import os
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
import httpx

from app.core.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class SupabaseClient:
    """Supabase client for database and storage operations."""
    
    def __init__(self):
        """Initialize Supabase client."""
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
            logger.warning("Supabase configuration missing")
            self.client = None
            return
        
        try:
            # Initialize with service role key for admin operations
            self.headers = {
                'apikey': settings.SUPABASE_SERVICE_ROLE_KEY,
                'Authorization': f'Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}',
                'Content-Type': 'application/json',
                'Prefer': 'return=minimal'
            }
            self.base_url = f"{settings.SUPABASE_URL}/rest/v1"
            self.storage_url = f"{settings.SUPABASE_URL}/storage/v1"
            self.client = True  # Mark client as initialized
            
            # Test connection
            with httpx.Client() as client:
                response = client.get(
                    f"{self.base_url}/",
                    headers=self.headers
                )
                if response.status_code == 200:
                    logger.info("Supabase client initialized successfully")
                else:
                    logger.error(f"Supabase connection failed: {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            self.client = None
    
    async def execute_query(self, table: str, method: str = "GET", 
                          params: Dict[str, Any] = None, 
                          data: Dict[str, Any] = None,
                          filters: str = None) -> Optional[List[Dict[str, Any]]]:
        """Execute a query on Supabase."""
        if not self.client:
            logger.error("Supabase client not available")
            return None
        
        try:
            url = f"{self.base_url}/{table}"
            if filters:
                url += f"?{filters}"
            
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    params=params,
                    json=data
                )
                
                if response.status_code in [200, 201]:
                    return response.json() if method != "DELETE" else True
                else:
                    logger.error(f"Query failed: {response.status_code} - {response.text}")
                    return None
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            return None
    
    async def get_user_profile(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        """Get user profile from Supabase."""
        filters = f"id=eq.{user_id}"
        result = await self.execute_query("profiles", filters=filters)
        return result[0] if result else None
    
    async def create_user_profile(self, user_id: UUID, profile_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create user profile in Supabase."""
        data = {"id": str(user_id), **profile_data}
        return await self.execute_query("profiles", method="POST", data=data)
    
    async def update_user_profile(self, user_id: UUID, profile_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update user profile in Supabase."""
        filters = f"id=eq.{user_id}"
        return await self.execute_query("profiles", method="PATCH", filters=filters, data=profile_data)
    
    async def get_projects(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Get user projects from Supabase."""
        filters = f"user_id=eq.{user_id}"
        result = await self.execute_query("projects", filters=filters)
        return result or []
    
    async def create_project(self, project_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create project in Supabase."""
        return await self.execute_query("projects", method="POST", data=project_data)
    
    async def get_education(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Get user education from Supabase."""
        filters = f"user_id=eq.{user_id}"
        result = await self.execute_query("education", filters=filters)
        return result or []
    
    async def create_education(self, education_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create education record in Supabase."""
        return await self.execute_query("education", method="POST", data=education_data)
    
    async def get_resumes(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Get user resumes from Supabase."""
        filters = f"user_id=eq.{user_id}"
        result = await self.execute_query("resume_versions", filters=filters)
        return result or []
    
    async def create_resume(self, resume_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create resume in Supabase."""
        return await self.execute_query("resume_versions", method="POST", data=resume_data)
    
    async def get_file_uploads(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Get user file uploads from Supabase."""
        filters = f"user_id=eq.{user_id}"
        result = await self.execute_query("file_uploads", filters=filters)
        return result or []
    
    async def create_file_upload(self, file_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create file upload record in Supabase."""
        return await self.execute_query("file_uploads", method="POST", data=file_data)
    
    # Storage operations
    async def upload_file_to_storage(self, bucket: str, file_path: str, file_content: bytes, 
                                   content_type: str = None) -> bool:
        """Upload file to Supabase Storage."""
        if not settings.SUPABASE_SERVICE_ROLE_KEY:
            logger.error("No Supabase service role key configured")
            return False
        
        try:
            url = f"{self.storage_url}/object/{bucket}/{file_path}"
            headers = {
                'apikey': settings.SUPABASE_SERVICE_ROLE_KEY,
                'Authorization': f'Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}',
                'Content-Type': content_type or 'application/octet-stream'
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    url,
                    headers=headers,
                    content=file_content
                )
                
                if response.status_code in [200, 201]:
                    logger.info(f"File uploaded to storage: {file_path}")
                    return True
                else:
                    logger.error(f"Storage upload failed: {response.status_code} - {response.text}")
                    return False
        except Exception as e:
            logger.error(f"Storage upload error: {e}")
            return False
    
    async def get_storage_url(self, bucket: str, file_path: str) -> Optional[str]:
        """Get public URL for storage file."""
        if not settings.SUPABASE_URL:
            return None
        
        return f"{settings.SUPABASE_URL}/storage/v1/object/public/{bucket}/{file_path}"
    
    async def delete_storage_file(self, bucket: str, file_path: str) -> bool:
        """Delete file from Supabase Storage."""
        try:
            url = f"{self.storage_url}/object/{bucket}/{file_path}"
            headers = {
                'apikey': settings.SUPABASE_SERVICE_ROLE_KEY,
                'Authorization': f'Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}'
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.delete(url, headers=headers)
                
                if response.status_code == 200:
                    logger.info(f"File deleted from storage: {file_path}")
                    return True
                else:
                    logger.error(f"Storage delete failed: {response.status_code} - {response.text}")
                    return False
        except Exception as e:
            logger.error(f"Storage delete error: {e}")
            return False


# Global Supabase client instance
supabase_client = SupabaseClient()