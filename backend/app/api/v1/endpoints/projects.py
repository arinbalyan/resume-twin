"""Project management endpoints."""

from fastapi import APIRouter, HTTPException, Query, status, UploadFile, File
from typing import List, Optional
from uuid import UUID

from app.services.project_service import ProjectService
from app.services import SupabaseService
from app.services.file_service import FileService
from app.models.projects import (
    Project, ProjectCreate, ProjectUpdate, ProjectWithMedia,
    ProjectMedia, ProjectMediaCreate, ProjectMediaUpdate,
    ProjectTechnology, ProjectTechnologyCreate,
    ProjectSummary, ProjectFilter, ProjectSearch, ProjectSearchResult
)
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
project_service = ProjectService()

router = APIRouter()


@router.get("/", response_model=List[ProjectSummary])
async def get_user_projects(
    user_id: UUID = Query(..., description="User ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status_filter: Optional[str] = Query(None, description="Filter by status", alias="status"),
    is_featured: Optional[bool] = Query(None, description="Filter featured projects"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get all projects for a user with optional filtering."""
    try:
        supabase = SupabaseService()
        query = supabase.client.table("projects").select("*").eq("user_id", str(user_id))
        
        if category:
            query = query.eq("category", category)
        if status_filter:
            query = query.eq("status", status_filter)
        if is_featured is not None:
            query = query.eq("is_featured", is_featured)
        
        result = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
        
        if result.data:
            # Get media and technology counts for each project
            projects = []
            for project_data in result.data:
                project_id = project_data["id"]
                
                # Count media
                media_result = supabase.client.table("project_media")\
                    .select("id", count="exact")\
                    .eq("project_id", project_id)\
                    .execute()
                media_count = len(media_result.data) if media_result.data else 0
                
                # Count technologies
                tech_result = supabase.client.table("project_technologies")\
                    .select("id", count="exact")\
                    .eq("project_id", project_id)\
                    .execute()
                tech_count = len(tech_result.data) if tech_result.data else 0
                
                projects.append(ProjectSummary(
                    **project_data,
                    media_count=media_count,
                    technology_count=tech_count
                ))
            
            return projects
        return []
    except Exception as e:
        logger.error(f"Error getting projects for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/", response_model=Project, status_code=status.HTTP_201_CREATED)
async def create_project(
    user_id: UUID = Query(..., description="User ID"),
    project_data: ProjectCreate = ...
):
    """Create new project."""
    try:
        project = project_service.create_project(user_id, project_data)
        if project:
            return project
        else:
            raise HTTPException(status_code=400, detail="Failed to create project")
    except Exception as e:
        logger.error(f"Error creating project for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{project_id}", response_model=ProjectWithMedia)
async def get_project(project_id: UUID):
    """Get specific project with all related data."""
    try:
        supabase = SupabaseService()
        
        # Get project
        project_result = supabase.client.table("projects")\
            .select("*")\
            .eq("id", str(project_id))\
            .execute()
        
        if not project_result.data:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project_data = project_result.data[0]
        
        # Get media
        media_result = supabase.client.table("project_media")\
            .select("*")\
            .eq("project_id", str(project_id))\
            .order("display_order")\
            .execute()
        
        # Get technologies
        tech_result = supabase.client.table("project_technologies")\
            .select("*")\
            .eq("project_id", str(project_id))\
            .execute()
        
        return ProjectWithMedia(
            **project_data,
            media=[ProjectMedia(**m) for m in (media_result.data or [])],
            technologies=[ProjectTechnology(**t) for t in (tech_result.data or [])]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{project_id}", response_model=Project)
async def update_project(project_id: UUID, project_data: ProjectUpdate):
    """Update project."""
    try:
        project = project_service.update_project(project_id, project_data)
        if project:
            return project
        else:
            raise HTTPException(status_code=404, detail="Project not found")
    except Exception as e:
        logger.error(f"Error updating project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: UUID):
    """Delete project."""
    try:
        success = project_service.delete_project(project_id)
        if not success:
            raise HTTPException(status_code=404, detail="Project not found")
    except Exception as e:
        logger.error(f"Error deleting project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================================
# PROJECT MEDIA ENDPOINTS
# ============================================================================

@router.get("/{project_id}/media", response_model=List[ProjectMedia])
async def get_project_media(project_id: UUID):
    """Get all media for a project."""
    try:
        supabase = SupabaseService()
        result = supabase.client.table("project_media")\
            .select("*")\
            .eq("project_id", str(project_id))\
            .order("display_order")\
            .execute()
        
        if result.data:
            return [ProjectMedia(**m) for m in result.data]
        return []
    except Exception as e:
        logger.error(f"Error getting media for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{project_id}/media", response_model=ProjectMedia, status_code=status.HTTP_201_CREATED)
async def upload_project_media(
    project_id: UUID,
    file: UploadFile = File(...),
    caption: Optional[str] = Query(None),
    alt_text: Optional[str] = Query(None),
    is_cover_image: bool = Query(False)
):
    """Upload project media file."""
    try:
        # Upload file to S3
        file_service = FileService()
        file_path = f"projects/{project_id}/media/{file.filename}"
        
        upload_result = await file_service.upload_file(
            file=file,
            file_path=file_path,
            user_id=None  # Project media doesn't need user_id tracking
        )
        
        # Create media record
        supabase = SupabaseService()
        media_data = {
            "project_id": str(project_id),
            "file_url": upload_result["file_url"],
            "file_name": file.filename,
            "file_size": upload_result["file_size"],
            "media_type": file.content_type,
            "caption": caption,
            "alt_text": alt_text,
            "is_cover_image": is_cover_image,
            "display_order": 0  # Will be updated if needed
        }
        
        result = supabase.client.table("project_media").insert(media_data).execute()
        
        if result.data:
            return ProjectMedia(**result.data[0])
        else:
            raise HTTPException(status_code=400, detail="Failed to create media record")
    except Exception as e:
        logger.error(f"Error uploading media for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{project_id}/media/{media_id}", response_model=ProjectMedia)
async def update_project_media(project_id: UUID, media_id: UUID, media_data: ProjectMediaUpdate):
    """Update project media metadata."""
    try:
        supabase = SupabaseService()
        update_dict = media_data.model_dump(exclude_unset=True)
        
        result = supabase.client.table("project_media")\
            .update(update_dict)\
            .eq("id", str(media_id))\
            .eq("project_id", str(project_id))\
            .execute()
        
        if result.data:
            return ProjectMedia(**result.data[0])
        else:
            raise HTTPException(status_code=404, detail="Media not found")
    except Exception as e:
        logger.error(f"Error updating media {media_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{project_id}/media/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_media(project_id: UUID, media_id: UUID):
    """Delete project media."""
    try:
        supabase = SupabaseService()
        
        # Get media to delete file from S3
        media_result = supabase.client.table("project_media")\
            .select("file_url")\
            .eq("id", str(media_id))\
            .execute()
        
        if media_result.data:
            # Delete from database
            delete_result = supabase.client.table("project_media")\
                .delete()\
                .eq("id", str(media_id))\
                .execute()
            
            if not delete_result.data:
                raise HTTPException(status_code=404, detail="Media not found")
                
            # TODO: Delete file from S3 storage
        else:
            raise HTTPException(status_code=404, detail="Media not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting media {media_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================================
# PROJECT TECHNOLOGIES ENDPOINTS
# ============================================================================

@router.get("/{project_id}/technologies", response_model=List[ProjectTechnology])
async def get_project_technologies(project_id: UUID):
    """Get all technologies for a project."""
    try:
        supabase = SupabaseService()
        result = supabase.client.table("project_technologies")\
            .select("*")\
            .eq("project_id", str(project_id))\
            .execute()
        
        if result.data:
            return [ProjectTechnology(**t) for t in result.data]
        return []
    except Exception as e:
        logger.error(f"Error getting technologies for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{project_id}/technologies", response_model=ProjectTechnology, status_code=status.HTTP_201_CREATED)
async def add_project_technology(project_id: UUID, tech_data: ProjectTechnologyCreate):
    """Add technology to a project."""
    try:
        supabase = SupabaseService()
        tech_dict = tech_data.model_dump()
        tech_dict["project_id"] = str(project_id)
        
        result = supabase.client.table("project_technologies").insert(tech_dict).execute()
        
        if result.data:
            return ProjectTechnology(**result.data[0])
        else:
            raise HTTPException(status_code=400, detail="Failed to add technology")
    except Exception as e:
        logger.error(f"Error adding technology to project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{project_id}/technologies/{tech_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_project_technology(project_id: UUID, tech_id: UUID):
    """Remove technology from a project."""
    try:
        supabase = SupabaseService()
        result = supabase.client.table("project_technologies")\
            .delete()\
            .eq("id", str(tech_id))\
            .eq("project_id", str(project_id))\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Technology not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing technology {tech_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")