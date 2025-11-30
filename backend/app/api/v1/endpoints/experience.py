"""Professional experience management endpoints (certifications, internships, courses, activities)."""

from fastapi import APIRouter, HTTPException, Query, status
from typing import List
from uuid import UUID

from app.services import SupabaseService
from app.models.experience import (
    Certification, CertificationCreate, CertificationUpdate,
    Internship, InternshipCreate, InternshipUpdate,
    Course, CourseCreate, CourseUpdate,
    Activity, ActivityCreate, ActivityUpdate,
    ExperienceSummary
)
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()

# ============================================================================
# CERTIFICATIONS
# ============================================================================

@router.get("/certifications", response_model=List[Certification], tags=["Certifications"])
async def get_user_certifications(
    user_id: UUID = Query(..., description="User ID"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get all certifications for a user."""
    try:
        supabase = SupabaseService()
        result = supabase.client.table("certifications")\
            .select("*")\
            .eq("user_id", str(user_id))\
            .order("issue_date", desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()
        
        if result.data:
            return [Certification(**cert) for cert in result.data]
        return []
    except Exception as e:
        logger.error(f"Error getting certifications for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/certifications", response_model=Certification, status_code=status.HTTP_201_CREATED, tags=["Certifications"])
async def create_certification(
    user_id: UUID = Query(..., description="User ID"),
    cert_data: CertificationCreate = ...
):
    """Create new certification entry."""
    try:
        supabase = SupabaseService()
        cert_dict = cert_data.model_dump()
        cert_dict["user_id"] = str(user_id)
        
        result = supabase.client.table("certifications").insert(cert_dict).execute()
        
        if result.data:
            return Certification(**result.data[0])
        else:
            raise HTTPException(status_code=400, detail="Failed to create certification")
    except Exception as e:
        logger.error(f"Error creating certification for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/certifications/{cert_id}", response_model=Certification, tags=["Certifications"])
async def get_certification(cert_id: UUID):
    """Get specific certification."""
    try:
        supabase = SupabaseService()
        result = supabase.client.table("certifications")\
            .select("*")\
            .eq("id", str(cert_id))\
            .execute()
        
        if result.data:
            return Certification(**result.data[0])
        else:
            raise HTTPException(status_code=404, detail="Certification not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting certification {cert_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/certifications/{cert_id}", response_model=Certification, tags=["Certifications"])
async def update_certification(cert_id: UUID, cert_data: CertificationUpdate):
    """Update certification."""
    try:
        supabase = SupabaseService()
        update_dict = cert_data.model_dump(exclude_unset=True)
        
        result = supabase.client.table("certifications")\
            .update(update_dict)\
            .eq("id", str(cert_id))\
            .execute()
        
        if result.data:
            return Certification(**result.data[0])
        else:
            raise HTTPException(status_code=404, detail="Certification not found")
    except Exception as e:
        logger.error(f"Error updating certification {cert_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/certifications/{cert_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Certifications"])
async def delete_certification(cert_id: UUID):
    """Delete certification."""
    try:
        supabase = SupabaseService()
        result = supabase.client.table("certifications")\
            .delete()\
            .eq("id", str(cert_id))\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Certification not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting certification {cert_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================================
# INTERNSHIPS
# ============================================================================

@router.get("/internships", response_model=List[Internship], tags=["Internships"])
async def get_user_internships(
    user_id: UUID = Query(..., description="User ID"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get all internships for a user."""
    try:
        supabase = SupabaseService()
        result = supabase.client.table("internships")\
            .select("*")\
            .eq("user_id", str(user_id))\
            .order("start_date", desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()
        
        if result.data:
            return [Internship(**intern) for intern in result.data]
        return []
    except Exception as e:
        logger.error(f"Error getting internships for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/internships", response_model=Internship, status_code=status.HTTP_201_CREATED, tags=["Internships"])
async def create_internship(
    user_id: UUID = Query(..., description="User ID"),
    internship_data: InternshipCreate = ...
):
    """Create new internship entry."""
    try:
        supabase = SupabaseService()
        intern_dict = internship_data.model_dump()
        intern_dict["user_id"] = str(user_id)
        
        result = supabase.client.table("internships").insert(intern_dict).execute()
        
        if result.data:
            return Internship(**result.data[0])
        else:
            raise HTTPException(status_code=400, detail="Failed to create internship")
    except Exception as e:
        logger.error(f"Error creating internship for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/internships/{internship_id}", response_model=Internship, tags=["Internships"])
async def get_internship(internship_id: UUID):
    """Get specific internship."""
    try:
        supabase = SupabaseService()
        result = supabase.client.table("internships")\
            .select("*")\
            .eq("id", str(internship_id))\
            .execute()
        
        if result.data:
            return Internship(**result.data[0])
        else:
            raise HTTPException(status_code=404, detail="Internship not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting internship {internship_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/internships/{internship_id}", response_model=Internship, tags=["Internships"])
async def update_internship(internship_id: UUID, internship_data: InternshipUpdate):
    """Update internship."""
    try:
        supabase = SupabaseService()
        update_dict = internship_data.model_dump(exclude_unset=True)
        
        result = supabase.client.table("internships")\
            .update(update_dict)\
            .eq("id", str(internship_id))\
            .execute()
        
        if result.data:
            return Internship(**result.data[0])
        else:
            raise HTTPException(status_code=404, detail="Internship not found")
    except Exception as e:
        logger.error(f"Error updating internship {internship_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/internships/{internship_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Internships"])
async def delete_internship(internship_id: UUID):
    """Delete internship."""
    try:
        supabase = SupabaseService()
        result = supabase.client.table("internships")\
            .delete()\
            .eq("id", str(internship_id))\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Internship not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting internship {internship_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================================
# COURSES
# ============================================================================

@router.get("/courses", response_model=List[Course], tags=["Courses"])
async def get_user_courses(
    user_id: UUID = Query(..., description="User ID"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get all courses for a user."""
    try:
        supabase = SupabaseService()
        result = supabase.client.table("courses")\
            .select("*")\
            .eq("user_id", str(user_id))\
            .order("completion_date", desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()
        
        if result.data:
            return [Course(**course) for course in result.data]
        return []
    except Exception as e:
        logger.error(f"Error getting courses for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/courses", response_model=Course, status_code=status.HTTP_201_CREATED, tags=["Courses"])
async def create_course(
    user_id: UUID = Query(..., description="User ID"),
    course_data: CourseCreate = ...
):
    """Create new course entry."""
    try:
        supabase = SupabaseService()
        course_dict = course_data.model_dump()
        course_dict["user_id"] = str(user_id)
        
        result = supabase.client.table("courses").insert(course_dict).execute()
        
        if result.data:
            return Course(**result.data[0])
        else:
            raise HTTPException(status_code=400, detail="Failed to create course")
    except Exception as e:
        logger.error(f"Error creating course for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/courses/{course_id}", response_model=Course, tags=["Courses"])
async def get_course(course_id: UUID):
    """Get specific course."""
    try:
        supabase = SupabaseService()
        result = supabase.client.table("courses")\
            .select("*")\
            .eq("id", str(course_id))\
            .execute()
        
        if result.data:
            return Course(**result.data[0])
        else:
            raise HTTPException(status_code=404, detail="Course not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting course {course_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/courses/{course_id}", response_model=Course, tags=["Courses"])
async def update_course(course_id: UUID, course_data: CourseUpdate):
    """Update course."""
    try:
        supabase = SupabaseService()
        update_dict = course_data.model_dump(exclude_unset=True)
        
        result = supabase.client.table("courses")\
            .update(update_dict)\
            .eq("id", str(course_id))\
            .execute()
        
        if result.data:
            return Course(**result.data[0])
        else:
            raise HTTPException(status_code=404, detail="Course not found")
    except Exception as e:
        logger.error(f"Error updating course {course_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Courses"])
async def delete_course(course_id: UUID):
    """Delete course."""
    try:
        supabase = SupabaseService()
        result = supabase.client.table("courses")\
            .delete()\
            .eq("id", str(course_id))\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Course not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting course {course_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================================
# ACTIVITIES
# ============================================================================

@router.get("/activities", response_model=List[Activity], tags=["Activities"])
async def get_user_activities(
    user_id: UUID = Query(..., description="User ID"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get all activities for a user."""
    try:
        supabase = SupabaseService()
        result = supabase.client.table("activities")\
            .select("*")\
            .eq("user_id", str(user_id))\
            .order("start_date", desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()
        
        if result.data:
            return [Activity(**activity) for activity in result.data]
        return []
    except Exception as e:
        logger.error(f"Error getting activities for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/activities", response_model=Activity, status_code=status.HTTP_201_CREATED, tags=["Activities"])
async def create_activity(
    user_id: UUID = Query(..., description="User ID"),
    activity_data: ActivityCreate = ...
):
    """Create new activity entry."""
    try:
        supabase = SupabaseService()
        activity_dict = activity_data.model_dump()
        activity_dict["user_id"] = str(user_id)
        
        result = supabase.client.table("activities").insert(activity_dict).execute()
        
        if result.data:
            return Activity(**result.data[0])
        else:
            raise HTTPException(status_code=400, detail="Failed to create activity")
    except Exception as e:
        logger.error(f"Error creating activity for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/activities/{activity_id}", response_model=Activity, tags=["Activities"])
async def get_activity(activity_id: UUID):
    """Get specific activity."""
    try:
        supabase = SupabaseService()
        result = supabase.client.table("activities")\
            .select("*")\
            .eq("id", str(activity_id))\
            .execute()
        
        if result.data:
            return Activity(**result.data[0])
        else:
            raise HTTPException(status_code=404, detail="Activity not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting activity {activity_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/activities/{activity_id}", response_model=Activity, tags=["Activities"])
async def update_activity(activity_id: UUID, activity_data: ActivityUpdate):
    """Update activity."""
    try:
        supabase = SupabaseService()
        update_dict = activity_data.model_dump(exclude_unset=True)
        
        result = supabase.client.table("activities")\
            .update(update_dict)\
            .eq("id", str(activity_id))\
            .execute()
        
        if result.data:
            return Activity(**result.data[0])
        else:
            raise HTTPException(status_code=404, detail="Activity not found")
    except Exception as e:
        logger.error(f"Error updating activity {activity_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/activities/{activity_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Activities"])
async def delete_activity(activity_id: UUID):
    """Delete activity."""
    try:
        supabase = SupabaseService()
        result = supabase.client.table("activities")\
            .delete()\
            .eq("id", str(activity_id))\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Activity not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting activity {activity_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================================
# COMPREHENSIVE EXPERIENCE SUMMARY
# ============================================================================

@router.get("/summary", response_model=ExperienceSummary, tags=["Experience Summary"])
async def get_experience_summary(user_id: UUID = Query(..., description="User ID")):
    """Get comprehensive experience summary for a user."""
    try:
        supabase = SupabaseService()
        
        # Fetch all experience data in parallel
        certifications_result = supabase.client.table("certifications")\
            .select("*")\
            .eq("user_id", str(user_id))\
            .execute()
        
        internships_result = supabase.client.table("internships")\
            .select("*")\
            .eq("user_id", str(user_id))\
            .execute()
        
        courses_result = supabase.client.table("courses")\
            .select("*")\
            .eq("user_id", str(user_id))\
            .execute()
        
        activities_result = supabase.client.table("activities")\
            .select("*")\
            .eq("user_id", str(user_id))\
            .execute()
        
        return ExperienceSummary(
            certifications=[Certification(**cert) for cert in (certifications_result.data or [])],
            internships=[Internship(**intern) for intern in (internships_result.data or [])],
            courses=[Course(**course) for course in (courses_result.data or [])],
            activities=[Activity(**activity) for activity in (activities_result.data or [])]
        )
    except Exception as e:
        logger.error(f"Error getting experience summary for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
