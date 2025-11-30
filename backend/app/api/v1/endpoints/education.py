"""Education management endpoints."""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List
from uuid import UUID

from app.services import SupabaseService
from app.models.user import Education, EducationCreate, EducationUpdate
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


@router.get("/", response_model=List[Education])
async def get_user_education(
    user_id: UUID = Query(..., description="User ID"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get all education entries for a user."""
    try:
        supabase = SupabaseService()
        result = supabase.client.table("education")\
            .select("*")\
            .eq("user_id", str(user_id))\
            .order("graduation_year", desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()
        
        if result.data:
            return [Education(**edu) for edu in result.data]
        return []
    except Exception as e:
        logger.error(f"Error getting education for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/", response_model=Education, status_code=status.HTTP_201_CREATED)
async def create_education(
    user_id: UUID = Query(..., description="User ID"),
    education_data: EducationCreate = ...
):
    """Create new education entry."""
    try:
        supabase = SupabaseService()
        edu_dict = education_data.model_dump()
        edu_dict["user_id"] = str(user_id)
        
        result = supabase.client.table("education").insert(edu_dict).execute()
        
        if result.data:
            return Education(**result.data[0])
        else:
            raise HTTPException(status_code=400, detail="Failed to create education entry")
    except Exception as e:
        logger.error(f"Error creating education for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{education_id}", response_model=Education)
async def get_education(education_id: UUID):
    """Get specific education entry."""
    try:
        supabase = SupabaseService()
        result = supabase.client.table("education")\
            .select("*")\
            .eq("id", str(education_id))\
            .execute()
        
        if result.data:
            return Education(**result.data[0])
        else:
            raise HTTPException(status_code=404, detail="Education entry not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting education {education_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{education_id}", response_model=Education)
async def update_education(education_id: UUID, education_data: EducationUpdate):
    """Update education entry."""
    try:
        supabase = SupabaseService()
        update_dict = education_data.model_dump(exclude_unset=True)
        
        result = supabase.client.table("education")\
            .update(update_dict)\
            .eq("id", str(education_id))\
            .execute()
        
        if result.data:
            return Education(**result.data[0])
        else:
            raise HTTPException(status_code=404, detail="Education entry not found")
    except Exception as e:
        logger.error(f"Error updating education {education_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{education_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_education(education_id: UUID):
    """Delete education entry."""
    try:
        supabase = SupabaseService()
        result = supabase.client.table("education")\
            .delete()\
            .eq("id", str(education_id))\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Education entry not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting education {education_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
