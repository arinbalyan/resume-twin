"""Resume generation endpoints."""

from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
import io

from app.services.pdf_service import pdf_service
from app.services.supabase_service import supabase_service
from app.core.exceptions import ResumeGenerationError

router = APIRouter()


class GenerateResumeRequest(BaseModel):
    """Request model for resume generation."""
    template_name: str = Field(..., description="Name of the LaTeX template to use")
    title: str = Field(..., description="Title for this resume version")
    selected_project_ids: Optional[List[str]] = Field(default=None, description="Specific project IDs to include")
    selected_tags: Optional[List[str]] = Field(default=None, description="Tags to filter projects by")
    customizations: Optional[Dict[str, Any]] = Field(default=None, description="Custom settings for the resume")
    job_description: Optional[str] = Field(default=None, description="Job description for optimization")


class ResumeResponse(BaseModel):
    """Response model for resume."""
    id: str
    title: str
    template_id: Optional[str]
    pdf_url: Optional[str]
    status: str
    created_at: str
    selected_project_ids: List[str]
    selected_tags: List[str]


@router.post("/generate")
async def generate_resume(
    request: GenerateResumeRequest,
    user_id: str = Depends(lambda: "temp_user")  # TODO: Replace with actual auth
) -> Dict[str, Any]:
    """Generate new resume PDF from template and user data."""
    try:
        # Fetch user profile data
        user_data = await supabase_service.get_user_profile(user_id)
        if not user_data:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Fetch education
        education_data = await supabase_service.get_user_education(user_id)
        user_data['education_items'] = education_data
        
        # Fetch experience (internships, certifications, etc.)
        experience_data = await supabase_service.get_user_experience(user_id)
        user_data['experience_items'] = experience_data
        
        # Generate PDF
        result = await pdf_service.generate_resume_pdf(
            user_id=user_id,
            template_name=request.template_name,
            user_data=user_data,
            selected_project_ids=request.selected_project_ids,
            selected_tags=request.selected_tags
        )
        
        if not result['success']:
            raise HTTPException(status_code=500, detail="Failed to generate resume PDF")
        
        # Save resume version to database
        # Find template ID
        template_id = None  # TODO: Get template ID from database
        
        saved_version = await pdf_service.save_resume_version(
            user_id=user_id,
            template_id=template_id,
            title=request.title,
            latex_content=result['latex_content'],
            pdf_url=result['pdf_url'],
            selected_project_ids=request.selected_project_ids,
            selected_tags=request.selected_tags,
            customizations=request.customizations
        )
        
        return {
            "success": True,
            "resume_id": saved_version.get('id'),
            "pdf_url": result['pdf_url'],
            "filename": result['filename'],
            "size": result['size'],
            "message": "Resume generated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate resume: {str(e)}")


@router.get("/")
async def get_resumes(
    user_id: str = Depends(lambda: "temp_user")  # TODO: Replace with actual auth
) -> List[ResumeResponse]:
    """Get all user resumes."""
    try:
        resumes = await supabase_service.get_user_resumes(user_id)
        return resumes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch resumes: {str(e)}")


@router.get("/{resume_id}")
async def get_resume(
    resume_id: str,
    user_id: str = Depends(lambda: "temp_user")  # TODO: Replace with actual auth
) -> Dict[str, Any]:
    """Get specific resume by ID."""
    try:
        resume = await supabase_service.get_resume_by_id(resume_id, user_id)
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        return resume
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch resume: {str(e)}")


@router.put("/{resume_id}")
async def update_resume(
    resume_id: str,
    request: GenerateResumeRequest,
    user_id: str = Depends(lambda: "temp_user")  # TODO: Replace with actual auth
) -> Dict[str, Any]:
    """Update existing resume."""
    try:
        # Check if resume exists
        existing = await supabase_service.get_resume_by_id(resume_id, user_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        # Regenerate PDF
        user_data = await supabase_service.get_user_profile(user_id)
        education_data = await supabase_service.get_user_education(user_id)
        user_data['education_items'] = education_data
        
        result = await pdf_service.generate_resume_pdf(
            user_id=user_id,
            template_name=request.template_name,
            user_data=user_data,
            selected_project_ids=request.selected_project_ids,
            selected_tags=request.selected_tags
        )
        
        # Update in database
        updated = await supabase_service.update_resume_version(
            resume_id=resume_id,
            updates={
                'title': request.title,
                'latex_content': result['latex_content'],
                'pdf_url': result['pdf_url'],
                'selected_project_ids': request.selected_project_ids or [],
                'selected_tags': request.selected_tags or [],
                'customizations': request.customizations or {}
            }
        )
        
        return {
            "success": True,
            "resume": updated,
            "message": "Resume updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update resume: {str(e)}")


@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: str,
    user_id: str = Depends(lambda: "temp_user")  # TODO: Replace with actual auth
) -> Dict[str, str]:
    """Delete resume."""
    try:
        await supabase_service.delete_resume(resume_id, user_id)
        return {"message": "Resume deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete resume: {str(e)}")


@router.post("/{resume_id}/optimize")
async def optimize_resume(
    resume_id: str,
    job_description: str,
    user_id: str = Depends(lambda: "temp_user")  # TODO: Replace with actual auth
) -> Dict[str, Any]:
    """Optimize resume with AI based on job description."""
    try:
        # TODO: Implement AI optimization
        raise HTTPException(status_code=501, detail="AI optimization coming soon")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to optimize resume: {str(e)}")


@router.get("/{resume_id}/download")
async def download_resume(
    resume_id: str,
    user_id: str = Depends(lambda: "temp_user")  # TODO: Replace with actual auth
) -> StreamingResponse:
    """Download resume PDF."""
    try:
        # Get resume from database
        resume = await supabase_service.get_resume_by_id(resume_id, user_id)
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        # If PDF URL exists, redirect or stream from S3
        if resume.get('pdf_url'):
            # For now, return the URL
            # TODO: Stream from S3 or return redirect
            return {"pdf_url": resume['pdf_url']}
        
        # Regenerate PDF if not available
        if resume.get('latex_content'):
            pdf_bytes = latex_service.compile_latex(resume['latex_content'], f"resume_{resume_id}")
            
            # Create streaming response
            pdf_stream = io.BytesIO(pdf_bytes)
            return StreamingResponse(
                pdf_stream,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename=resume_{resume_id}.pdf"
                }
            )
        
        raise HTTPException(status_code=404, detail="PDF not available")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download resume: {str(e)}")


@router.get("/templates/list")
async def list_templates() -> Dict[str, Any]:
    """Get list of available resume templates and generation method info."""
    try:
        templates = pdf_service.get_available_templates()
        method_status = pdf_service.get_generation_method_status()
        
        return {
            "templates": templates,
            "generation_method": method_status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch templates: {str(e)}")


@router.get("/generation-methods/status")
async def get_generation_methods_status() -> Dict[str, Any]:
    """Get status and availability of all PDF generation methods."""
    try:
        return pdf_service.get_generation_method_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get method status: {str(e)}")