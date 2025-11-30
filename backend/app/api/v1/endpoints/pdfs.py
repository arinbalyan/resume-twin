"""PDF management endpoints - Generate, store, and download PDFs."""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
import time
import io

from app.utils.logger import setup_logger
from app.services.pdf_storage_service import pdf_storage_service
from app.services.html_to_pdf_service import html_to_pdf_service
from app.services.template_service import template_service
from app.core.config import settings

logger = setup_logger(__name__)
router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class GeneratePDFRequest(BaseModel):
    """Request to generate a PDF from a template."""
    template_name: str = Field(..., description="Name of the HTML template to use")
    file_name: Optional[str] = Field(None, description="Custom file name for the PDF")
    resume_version_id: Optional[UUID] = Field(None, description="Link to a resume version")
    expires_in_days: Optional[int] = Field(None, description="Days until PDF expires (None = never)")
    
    # Template data (optional - override template defaults)
    name: Optional[str] = None
    title: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None


class PDFResponse(BaseModel):
    """PDF metadata response."""
    pdf_id: str
    file_name: str
    file_size: int
    template_name: Optional[str]
    download_url: Optional[str]
    created_at: Optional[str]
    expires_at: Optional[str]


class PDFListResponse(BaseModel):
    """List of user's PDFs."""
    pdfs: List[PDFResponse]
    total: int


class DownloadURLResponse(BaseModel):
    """Presigned download URL response."""
    url: str
    expires_in: int
    file_name: str


class TogglePublicRequest(BaseModel):
    """Request to toggle public sharing."""
    is_public: bool


class TogglePublicResponse(BaseModel):
    """Response for toggle public."""
    is_public: bool
    public_url: Optional[str] = None


class StorageStatsResponse(BaseModel):
    """User storage statistics."""
    total_pdfs: int
    total_storage_bytes: int
    total_storage_mb: float


# ============================================================================
# Authentication Dependency (simplified for demo)
# ============================================================================

async def get_current_user_id(request: Request) -> UUID:
    """
    Get the current authenticated user's ID.
    
    In production, this would validate the JWT token from Supabase.
    For demo purposes, we'll accept a user_id header.
    """
    # Try to get from Authorization header (JWT token)
    auth_header = request.headers.get("Authorization")
    
    if auth_header and auth_header.startswith("Bearer "):
        # In production: decode JWT and extract user_id
        # For now, we'll use a demo user_id from headers
        pass
    
    # Demo: Accept user_id from header
    user_id_header = request.headers.get("X-User-ID")
    if user_id_header:
        try:
            return UUID(user_id_header)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID format"
            )
    
    # Default demo user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required. Provide X-User-ID header or Authorization Bearer token."
    )


# ============================================================================
# PDF Generation & Storage Endpoints
# ============================================================================

@router.post("/generate", response_model=PDFResponse, status_code=status.HTTP_201_CREATED)
async def generate_and_store_pdf(
    request: GeneratePDFRequest,
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Generate a PDF from an HTML template and store it in Supabase Storage.
    
    The generated PDF is associated with the authenticated user and can only
    be downloaded by that user (unless made public).
    """
    start_time = time.time()
    
    # Check if PDF generation is available
    pdf_status = html_to_pdf_service.get_status()
    if not pdf_status["pdf_available"]:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"PDF generation not available. Configure one of: {', '.join(pdf_status['available_methods'])}"
        )
    
    # Load the template
    template_content = template_service.get_template(request.template_name, "html")
    if not template_content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template '{request.template_name}' not found"
        )
    
    # Prepare template data
    template_data = {
        "name": request.name or "John Doe",
        "title": request.title or "Software Developer",
        "email": request.email or "john.doe@email.com",
        "phone": request.phone or "(555) 123-4567",
        "location": request.location or "San Francisco, CA",
        "summary": request.summary or "Experienced software developer with a passion for building scalable applications."
    }
    
    # Render template with data
    rendered_html = template_service.render_template(template_content, template_data)
    
    # Generate PDF
    pdf_result = await html_to_pdf_service.generate_pdf(rendered_html)
    
    if not pdf_result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF generation failed: {pdf_result.get('error', 'Unknown error')}"
        )
    
    generation_time_ms = int((time.time() - start_time) * 1000)
    
    # Generate file name
    file_name = request.file_name or f"{template_data['name'].replace(' ', '_')}_Resume.pdf"
    if not file_name.endswith('.pdf'):
        file_name += '.pdf'
    
    # Store PDF in Supabase Storage
    storage_result = await pdf_storage_service.store_pdf(
        pdf_content=pdf_result["content"],
        user_id=user_id,
        file_name=file_name,
        template_name=request.template_name,
        template_type="html",
        generation_method=pdf_result.get("method", "unknown"),
        generation_time_ms=generation_time_ms,
        resume_version_id=request.resume_version_id,
        expires_in_days=request.expires_in_days
    )
    
    if not storage_result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store PDF: {storage_result.get('error', 'Unknown error')}"
        )
    
    # Generate download URL
    download_url = await pdf_storage_service.get_download_url(
        pdf_id=UUID(storage_result["pdf_id"]),
        user_id=user_id,
        expires_in=3600  # 1 hour
    )
    
    return PDFResponse(
        pdf_id=storage_result["pdf_id"],
        file_name=file_name,
        file_size=storage_result["file_size"],
        template_name=request.template_name,
        download_url=download_url,
        created_at=None,  # Will be set by database
        expires_at=storage_result.get("expires_at")
    )


@router.get("/my-pdfs", response_model=PDFListResponse)
async def list_my_pdfs(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user_id: UUID = Depends(get_current_user_id)
):
    """
    List all PDFs belonging to the authenticated user.
    """
    pdfs = await pdf_storage_service.list_user_pdfs(
        user_id=user_id,
        limit=limit,
        offset=offset
    )
    
    pdf_responses = []
    for pdf in pdfs:
        pdf_responses.append(PDFResponse(
            pdf_id=pdf["id"],
            file_name=pdf["file_name"],
            file_size=pdf["file_size"],
            template_name=pdf.get("template_name"),
            download_url=None,  # Will be generated on demand
            created_at=pdf.get("created_at"),
            expires_at=None
        ))
    
    return PDFListResponse(pdfs=pdf_responses, total=len(pdfs))


@router.get("/{pdf_id}/download-url", response_model=DownloadURLResponse)
async def get_pdf_download_url(
    pdf_id: UUID,
    expires_in: int = Query(default=3600, ge=60, le=86400, description="URL expiration in seconds"),
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Get a presigned download URL for a PDF.
    
    The URL is valid for the specified duration (default 1 hour, max 24 hours).
    Only the owner of the PDF can request a download URL.
    """
    url = await pdf_storage_service.get_download_url(
        pdf_id=pdf_id,
        user_id=user_id,
        expires_in=expires_in
    )
    
    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF not found or you don't have permission to access it"
        )
    
    return DownloadURLResponse(
        url=url,
        expires_in=expires_in,
        file_name="resume.pdf"  # Will be replaced with actual name
    )


@router.get("/{pdf_id}/download")
async def download_pdf(
    pdf_id: UUID,
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Download a PDF directly (streams the file content).
    
    Only the owner of the PDF can download it.
    """
    result = await pdf_storage_service.download_pdf(
        pdf_id=pdf_id,
        user_id=user_id
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF not found or you don't have permission to access it"
        )
    
    # Stream the PDF content
    return StreamingResponse(
        io.BytesIO(result["content"]),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{result["file_name"]}"',
            "Content-Length": str(result["file_size"])
        }
    )


@router.delete("/{pdf_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pdf(
    pdf_id: UUID,
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Delete a PDF and its storage.
    
    Only the owner of the PDF can delete it.
    """
    success = await pdf_storage_service.delete_pdf(
        pdf_id=pdf_id,
        user_id=user_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF not found or you don't have permission to delete it"
        )
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/{pdf_id}/public", response_model=TogglePublicResponse)
async def toggle_pdf_public(
    pdf_id: UUID,
    request: TogglePublicRequest,
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Toggle public sharing for a PDF.
    
    When a PDF is made public, anyone with the public link can download it.
    """
    result = await pdf_storage_service.toggle_public(
        pdf_id=pdf_id,
        user_id=user_id,
        is_public=request.is_public
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF not found or you don't have permission to modify it"
        )
    
    public_url = None
    if result["is_public"] and result.get("public_token"):
        public_url = f"{settings.SUPABASE_URL}/api/v1/pdfs/public/{result['public_token']}"
    
    return TogglePublicResponse(
        is_public=result["is_public"],
        public_url=public_url
    )


@router.get("/public/{public_token}")
async def download_public_pdf(public_token: UUID):
    """
    Download a publicly shared PDF using its public token.
    
    No authentication required for public PDFs.
    """
    result = await pdf_storage_service.get_public_download_url(public_token)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Public PDF not found or sharing has been disabled"
        )
    
    # Redirect to the presigned URL
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=result["url"])


@router.get("/stats", response_model=StorageStatsResponse)
async def get_storage_stats(
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Get storage statistics for the authenticated user.
    """
    stats = await pdf_storage_service.get_user_storage_stats(user_id)
    
    return StorageStatsResponse(
        total_pdfs=stats["total_pdfs"],
        total_storage_bytes=stats["total_storage_bytes"],
        total_storage_mb=stats.get("total_storage_mb", 0)
    )
