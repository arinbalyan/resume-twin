"""Profile management endpoints."""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from uuid import UUID
from app.services.profile_service import ProfileService
from app.services.github_service import github_service
from app.services.resume_scorer_service import resume_scorer
from app.models.user import Profile, ProfileCreate, ProfileUpdate, ProfileStats
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
profile_service = ProfileService()

router = APIRouter()


@router.get("/", response_model=List[Profile])
async def get_profiles(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    public_only: bool = Query(True)
):
    """Get user profiles with pagination."""
    try:
        if public_only:
            profiles = profile_service.get_public_profiles(limit, offset)
        else:
            # In production, this would require authentication
            raise HTTPException(status_code=401, detail="Authentication required")
        
        return profiles
    except Exception as e:
        logger.error(f"Error getting profiles: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/", response_model=Profile)
async def create_profile(profile_data: ProfileCreate):
    """Create new profile."""
    try:
        # In production, get user_id from authentication token
        # For now, using a placeholder UUID
        user_id = UUID("00000000-0000-0000-0000-000000000000")
        
        profile = profile_service.create_profile(user_id, profile_data)
        if profile:
            return profile
        else:
            raise HTTPException(status_code=400, detail="Failed to create profile")
    except Exception as e:
        logger.error(f"Error creating profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{profile_id}", response_model=Profile)
async def get_profile(profile_id: str):
    """Get specific profile."""
    try:
        profile = profile_service.get_profile(UUID(profile_id))
        if profile:
            # Check if profile is public or if user has permission
            if not profile.is_public:
                raise HTTPException(status_code=403, detail="Profile is private")
            return profile
        else:
            raise HTTPException(status_code=404, detail="Profile not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting profile {profile_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{profile_id}", response_model=Profile)
async def update_profile(profile_id: str, profile_data: ProfileUpdate):
    """Update profile."""
    try:
        # In production, verify user owns this profile
        profile = profile_service.update_profile(UUID(profile_id), profile_data)
        if profile:
            return profile
        else:
            raise HTTPException(status_code=404, detail="Profile not found")
    except Exception as e:
        logger.error(f"Error updating profile {profile_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{profile_id}")
async def delete_profile(profile_id: str):
    """Delete profile."""
    try:
        # In production, verify user owns this profile
        success = profile_service.delete_profile(UUID(profile_id))
        if success:
            return {"message": "Profile deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Profile not found")
    except Exception as e:
        logger.error(f"Error deleting profile {profile_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{profile_id}/stats", response_model=ProfileStats)
async def get_profile_stats(profile_id: str):
    """Get profile statistics."""
    try:
        stats = profile_service.get_profile_stats(UUID(profile_id))
        return stats
    except Exception as e:
        logger.error(f"Error getting profile stats for {profile_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/search/results", response_model=List[Profile])
async def search_profiles(
    q: str = Query(..., description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Search profiles by name, title, or bio."""
    try:
        profiles = profile_service.search_profiles(q, limit, offset)
        return profiles
    except Exception as e:
        logger.error(f"Error searching profiles with query '{q}': {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/featured/", response_model=List[Profile])
async def get_featured_profiles(limit: int = Query(10, ge=1, le=50)):
    """Get featured profiles."""
    try:
        profiles = profile_service.get_featured_profiles(limit)
        return profiles
    except Exception as e:
        logger.error(f"Error getting featured profiles: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/recent/", response_model=List[Profile])
async def get_recent_profiles(limit: int = Query(10, ge=1, le=50)):
    """Get recently created profiles."""
    try:
        profiles = profile_service.get_recent_profiles(limit)
        return profiles
    except Exception as e:
        logger.error(f"Error getting recent profiles: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{profile_id}/completion-score")
async def update_completion_score(profile_id: str):
    """Update profile completion score."""
    try:
        success = profile_service.update_profile_completion_score(UUID(profile_id))
        if success:
            return {"message": "Completion score updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Profile not found")
    except Exception as e:
        logger.error(f"Error updating completion score for {profile_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============== GitHub Integration ==============

@router.get("/github/{username}")
async def get_github_profile(username: str) -> Dict[str, Any]:
    """
    Fetch GitHub profile and repositories for a username.
    
    Returns:
    - User profile information
    - Top repositories by stars
    - Contribution statistics
    - Top programming languages
    """
    try:
        result = await github_service.get_complete_profile(username)
        
        if result.get("error"):
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching GitHub profile for {username}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch GitHub profile: {str(e)}")


@router.get("/github/{username}/repos")
async def get_github_repos(
    username: str,
    limit: int = Query(10, ge=1, le=100),
    sort: str = Query("stars", regex="^(stars|updated|pushed)$"),
    include_forks: bool = Query(False)
) -> Dict[str, Any]:
    """
    Fetch GitHub repositories for a username.
    
    Query Parameters:
    - limit: Maximum repos to return (1-100)
    - sort: Sort by stars, updated, or pushed
    - include_forks: Include forked repositories
    """
    try:
        repos = await github_service.get_user_repos(
            username, 
            limit=limit, 
            sort=sort, 
            include_forks=include_forks
        )
        
        return {
            "username": username,
            "count": len(repos),
            "repositories": repos
        }
    except Exception as e:
        logger.error(f"Error fetching GitHub repos for {username}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch GitHub repositories: {str(e)}")


@router.post("/github/{username}/import-projects")
async def import_github_projects(
    username: str,
    limit: int = Query(5, ge=1, le=20)
) -> Dict[str, Any]:
    """
    Import GitHub repositories as projects for resume.
    
    Converts top repositories to project format suitable for resume templates.
    """
    try:
        repos = await github_service.get_user_repos(username, limit=limit, sort="stars")
        
        if not repos:
            raise HTTPException(status_code=404, detail=f"No repositories found for {username}")
        
        projects = github_service.repos_to_projects(repos)
        
        return {
            "username": username,
            "imported_count": len(projects),
            "projects": projects,
            "message": f"Successfully converted {len(projects)} repositories to project format"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing GitHub projects for {username}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to import GitHub projects: {str(e)}")


@router.get("/github/status")
async def get_github_status() -> Dict[str, Any]:
    """Check GitHub API configuration status."""
    return {
        "configured": github_service.is_available(),
        "rate_limit": "5000/hour" if github_service.is_available() else "60/hour",
        "message": "GitHub token configured" if github_service.is_available() 
                   else "No GitHub token - limited to 60 requests/hour"
    }


# ============== Resume Scoring ==============

@router.post("/score-resume")
async def score_resume(
    resume_data: Dict[str, Any],
    job_description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Score a resume and get improvement suggestions.
    
    Request Body:
    - resume_data: Resume data with sections (summary, experience, skills, etc.)
    - job_description: Optional job description for keyword matching
    
    Returns:
    - Overall score (0-100)
    - Category scores
    - ATS compatibility score
    - Issues and suggestions
    - Keyword matches (if job description provided)
    """
    try:
        result = resume_scorer.score_resume(resume_data, job_description)
        
        return {
            "overall_score": result.overall_score,
            "ats_compatibility": result.ats_compatibility,
            "category_scores": result.category_scores,
            "issues": result.issues,
            "suggestions": result.suggestions,
            "keyword_matches": result.keyword_matches,
            "improvement_priorities": resume_scorer.get_improvement_priority(result)
        }
    except Exception as e:
        logger.error(f"Error scoring resume: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to score resume: {str(e)}")