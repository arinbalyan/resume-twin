"""Overleaf API service for LaTeX compilation."""

import logging
import httpx
from typing import Dict, Any, Optional
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)


class OverleafApiService:
    """Service for compiling LaTeX documents using Overleaf API."""

    def __init__(self):
        """Initialize the Overleaf API service."""
        self.api_url = settings.OVERLEAF_API_URL
        self.api_token = settings.OVERLEAF_API_TOKEN
        self.template_id = settings.OVERLEAF_TEMPLATE_ID
        self.timeout = settings.LATEX_COMPILATION_TIMEOUT
        
        if not self.api_url or not self.api_token:
            logger.warning("Overleaf API credentials not configured")
        else:
            logger.info(f"Overleaf API service initialized with URL: {self.api_url}")

    def is_available(self) -> bool:
        """
        Check if Overleaf API is configured and available.

        Returns:
            True if API credentials are configured, False otherwise
        """
        return bool(self.api_url and self.api_token)

    async def compile_latex(
        self,
        latex_content: str,
        project_name: str = "Resume",
        compiler: str = "pdflatex"
    ) -> bytes:
        """
        Compile LaTeX document using Overleaf API.

        Args:
            latex_content: LaTeX source code
            project_name: Name for the project
            compiler: LaTeX compiler to use (pdflatex, xelatex, lualatex)

        Returns:
            Compiled PDF as bytes

        Raises:
            ValueError: If API not configured
            httpx.HTTPError: If API request fails
            Exception: If compilation fails
        """
        if not self.is_available():
            raise ValueError("Overleaf API credentials not configured")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Create project
                project_id = await self._create_project(client, project_name)
                
                # Upload LaTeX file
                await self._upload_file(client, project_id, "main.tex", latex_content)
                
                # Compile project
                pdf_bytes = await self._compile_project(client, project_id, compiler)
                
                # Cleanup project (optional)
                await self._delete_project(client, project_id)
                
                logger.info(f"Successfully compiled LaTeX document using Overleaf API ({len(pdf_bytes)} bytes)")
                return pdf_bytes
                
        except Exception as e:
            logger.error(f"Overleaf API compilation failed: {str(e)}")
            raise

    async def _create_project(self, client: httpx.AsyncClient, project_name: str) -> str:
        """
        Create a new Overleaf project.

        Args:
            client: HTTP client
            project_name: Name for the project

        Returns:
            Project ID

        Raises:
            httpx.HTTPError: If API request fails
        """
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "projectName": project_name,
            "template": self.template_id if self.template_id else "blank"
        }
        
        response = await client.post(
            f"{self.api_url}/project/new",
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        
        data = response.json()
        project_id = data.get("project_id")
        
        logger.info(f"Created Overleaf project: {project_id}")
        return project_id

    async def _upload_file(
        self,
        client: httpx.AsyncClient,
        project_id: str,
        filename: str,
        content: str
    ) -> None:
        """
        Upload file to Overleaf project.

        Args:
            client: HTTP client
            project_id: Project ID
            filename: Name of the file
            content: File content

        Raises:
            httpx.HTTPError: If API request fails
        """
        headers = {
            "Authorization": f"Bearer {self.api_token}"
        }
        
        files = {
            "file": (filename, content.encode('utf-8'), "text/plain")
        }
        
        response = await client.post(
            f"{self.api_url}/project/{project_id}/upload",
            files=files,
            headers=headers
        )
        response.raise_for_status()
        
        logger.info(f"Uploaded file '{filename}' to project {project_id}")

    async def _compile_project(
        self,
        client: httpx.AsyncClient,
        project_id: str,
        compiler: str = "pdflatex"
    ) -> bytes:
        """
        Compile Overleaf project.

        Args:
            client: HTTP client
            project_id: Project ID
            compiler: LaTeX compiler

        Returns:
            Compiled PDF as bytes

        Raises:
            httpx.HTTPError: If API request fails
            Exception: If compilation fails
        """
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "compiler": compiler,
            "rootDoc_id": "main.tex"
        }
        
        # Trigger compilation
        response = await client.post(
            f"{self.api_url}/project/{project_id}/compile",
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        
        compile_data = response.json()
        
        # Check compilation status
        if compile_data.get("status") != "success":
            errors = compile_data.get("errors", [])
            error_msg = "\n".join([e.get("message", "") for e in errors[:5]])
            raise Exception(f"Compilation failed: {error_msg}")
        
        # Download PDF
        pdf_url = compile_data.get("output_files", [{}])[0].get("url")
        if not pdf_url:
            raise Exception("No PDF output found")
        
        pdf_response = await client.get(pdf_url, headers=headers)
        pdf_response.raise_for_status()
        
        logger.info(f"Compiled project {project_id} successfully")
        return pdf_response.content

    async def _delete_project(self, client: httpx.AsyncClient, project_id: str) -> None:
        """
        Delete Overleaf project.

        Args:
            client: HTTP client
            project_id: Project ID

        Raises:
            httpx.HTTPError: If API request fails
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_token}"
            }
            
            response = await client.delete(
                f"{self.api_url}/project/{project_id}",
                headers=headers
            )
            response.raise_for_status()
            
            logger.info(f"Deleted Overleaf project: {project_id}")
        except Exception as e:
            logger.warning(f"Failed to delete Overleaf project {project_id}: {str(e)}")


# Global instance
overleaf_service = OverleafApiService()
