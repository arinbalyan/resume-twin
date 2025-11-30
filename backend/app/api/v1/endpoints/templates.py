"""Template management endpoints."""

from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import StreamingResponse, HTMLResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import io

from app.services.html_to_pdf_service import html_to_pdf_service
from app.services.pdf_service import pdf_service
from app.core.config import settings

router = APIRouter()


class TemplateResponse(BaseModel):
    """Response model for template info."""
    name: str
    display_name: str
    description: str
    path: str
    size: int


class TemplatePreviewRequest(BaseModel):
    """Request model for template preview with custom data."""
    custom_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Custom data to merge with sample data for preview"
    )


@router.get("/", response_model=Dict[str, Any])
async def get_templates():
    """Get all available resume templates with metadata."""
    try:
        # Get HTML templates
        html_templates = html_to_pdf_service.list_templates_with_info()
        
        # Get generation method status
        method_status = pdf_service.get_generation_method_status()
        
        # Get WeasyPrint status
        html_service_status = html_to_pdf_service.get_status()
        
        return {
            "templates": html_templates,
            "total_count": len(html_templates),
            "generation_method": settings.PDF_GENERATION_METHOD,
            "method_status": method_status,
            "html_pdf_status": html_service_status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch templates: {str(e)}")


@router.get("/status")
async def get_templates_status() -> Dict[str, Any]:
    """Get template system status including PDF generation capabilities."""
    try:
        method_status = pdf_service.get_generation_method_status()
        html_status = html_to_pdf_service.get_status()
        
        return {
            "pdf_generation_method": settings.PDF_GENERATION_METHOD,
            "method_status": method_status,
            "html_pdf_status": html_status,
            "recommendation": (
                "All systems ready" 
                if html_status["weasyprint_available"] 
                else "WeasyPrint not available. Consider using PDF_GENERATION_METHOD=latex in .env, or install GTK3 libraries."
            )
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@router.get("/sample-data")
async def get_sample_data() -> Dict[str, Any]:
    """Get sample resume data used for template previews."""
    return html_to_pdf_service.get_sample_data()


@router.get("/{template_name}")
async def get_template(template_name: str) -> Dict[str, Any]:
    """Get specific template info."""
    try:
        # Add .html extension if not present
        if not template_name.endswith('.html'):
            template_name = f"{template_name}.html"
        
        template_info = html_to_pdf_service.get_template_info(template_name)
        
        if not template_info:
            raise HTTPException(status_code=404, detail=f"Template '{template_name}' not found")
        
        return template_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch template: {str(e)}")


@router.get("/{template_name}/preview/html")
async def preview_template_html(
    template_name: str,
    user_name: Optional[str] = Query(None, description="Custom name for preview"),
    title: Optional[str] = Query(None, description="Custom title for preview")
) -> HTMLResponse:
    """Preview template as rendered HTML."""
    try:
        # Add .html extension if not present
        if not template_name.endswith('.html'):
            template_name = f"{template_name}.html"
        
        # Validate template exists
        if not html_to_pdf_service.validate_template_exists(template_name):
            raise HTTPException(status_code=404, detail=f"Template '{template_name}' not found")
        
        # Prepare custom data if provided
        custom_data = {}
        if user_name:
            custom_data['user_name'] = user_name
        if title:
            custom_data['title'] = title
        
        # Render HTML
        html_content = html_to_pdf_service.render_template_html(
            template_name, 
            custom_data if custom_data else None
        )
        
        return HTMLResponse(content=html_content)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to preview template: {str(e)}")


@router.get("/{template_name}/preview/pdf")
async def preview_template_pdf(
    template_name: str,
    user_name: Optional[str] = Query(None, description="Custom name for preview"),
    title: Optional[str] = Query(None, description="Custom title for preview")
) -> StreamingResponse:
    """Preview template as PDF with sample data."""
    try:
        # Check if PDF generation is available
        if not html_to_pdf_service.is_pdf_generation_available():
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "PDF generation not available",
                    "reason": "WeasyPrint requires GTK3 libraries which are not installed",
                    "solution": "Install GTK3 (see https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation) or use HTML preview instead",
                    "alternative": "Use the /preview/html endpoint to preview templates as HTML"
                }
            )
        
        # Add .html extension if not present
        if not template_name.endswith('.html'):
            template_name = f"{template_name}.html"
        
        # Validate template exists
        if not html_to_pdf_service.validate_template_exists(template_name):
            raise HTTPException(status_code=404, detail=f"Template '{template_name}' not found")
        
        # Prepare custom data if provided
        custom_data = {}
        if user_name:
            custom_data['user_name'] = user_name
        if title:
            custom_data['title'] = title
        
        # Generate preview PDF
        pdf_bytes = html_to_pdf_service.preview_template(
            template_name,
            custom_data if custom_data else None
        )
        
        # Return as streaming response
        pdf_stream = io.BytesIO(pdf_bytes)
        filename = f"preview_{template_name.replace('.html', '')}.pdf"
        
        return StreamingResponse(
            pdf_stream,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"inline; filename={filename}",
                "Content-Length": str(len(pdf_bytes))
            }
        )
        
    except HTTPException:
        raise
    except RuntimeError as e:
        # WeasyPrint not available error
        raise HTTPException(
            status_code=503, 
            detail={
                "error": "PDF generation not available",
                "message": str(e),
                "alternative": "Use the /preview/html endpoint"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate preview PDF: {str(e)}")


@router.post("/{template_name}/preview/pdf")
async def preview_template_with_custom_data(
    template_name: str,
    request: TemplatePreviewRequest
) -> StreamingResponse:
    """Preview template as PDF with custom data."""
    try:
        # Check if PDF generation is available
        if not html_to_pdf_service.is_pdf_generation_available():
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "PDF generation not available",
                    "reason": "WeasyPrint requires GTK3 libraries which are not installed",
                    "solution": "Install GTK3 or use HTML preview instead"
                }
            )
        
        # Add .html extension if not present
        if not template_name.endswith('.html'):
            template_name = f"{template_name}.html"
        
        # Validate template exists
        if not html_to_pdf_service.validate_template_exists(template_name):
            raise HTTPException(status_code=404, detail=f"Template '{template_name}' not found")
        
        # Generate preview PDF with custom data
        pdf_bytes = html_to_pdf_service.preview_template(
            template_name,
            request.custom_data
        )
        
        # Return as streaming response
        pdf_stream = io.BytesIO(pdf_bytes)
        filename = f"preview_{template_name.replace('.html', '')}.pdf"
        
        return StreamingResponse(
            pdf_stream,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"inline; filename={filename}",
                "Content-Length": str(len(pdf_bytes))
            }
        )
        
    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(
            status_code=503, 
            detail={
                "error": "PDF generation not available",
                "message": str(e)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate preview PDF: {str(e)}")


@router.post("/")
async def create_template():
    """Create new template (admin only)."""
    raise HTTPException(status_code=501, detail="Template creation not implemented yet")


@router.put("/{template_id}")
async def update_template(template_id: str):
    """Update template (admin only)."""
    raise HTTPException(status_code=501, detail="Template update not implemented yet")


@router.delete("/{template_id}")
async def delete_template(template_id: str):
    """Delete template (admin only)."""
    raise HTTPException(status_code=501, detail="Template deletion not implemented yet")


@router.post("/{template_id}/customize")
async def customize_template(template_id: str):
    """Customize template for user."""
    raise HTTPException(status_code=501, detail="Template customization not implemented yet")