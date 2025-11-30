"""
AI-powered resume optimization API endpoints.

This module provides REST API endpoints for AI-driven resume optimization,
job description analysis, and content suggestions.

Author: Resume Twin Development Team
Version: 1.0.0
"""

from typing import Dict, Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Body
from pydantic import BaseModel, Field, validator

from app.services.ai_service import (
    AIService,
    get_ai_service,
    JobAnalysis,
    ResumeOptimization,
    OptimizationLevel,
)
from app.core.exceptions import (
    AIServiceException,
    JobDescriptionInvalidError,
    JobParsingError,
    ResumeOptimizationException,
)
from app.utils.logger import setup_logger

# Initialize logger
logger = setup_logger(__name__)

# Create router
router = APIRouter(prefix="/ai", tags=["AI Optimization"])


# Request/Response Models

class JobDescriptionRequest(BaseModel):
    """
    Request model for job description analysis.
    
    Attributes:
        job_description: Full text of the job description to analyze
        extract_keywords: Whether to extract ATS keywords
    """
    
    job_description: str = Field(
        ...,
        min_length=50,
        max_length=10000,
        description="Job description text to analyze"
    )
    extract_keywords: bool = Field(
        default=True,
        description="Whether to extract ATS-optimized keywords"
    )
    
    @validator("job_description")
    def validate_job_description(cls, value: str) -> str:
        """Validate job description is not empty or whitespace."""
        if not value or not value.strip():
            raise ValueError("Job description cannot be empty")
        return value.strip()


class JobAnalysisResponse(BaseModel):
    """
    Response model for job description analysis.
    
    Attributes:
        success: Whether analysis was successful
        analysis: Structured job analysis data
        message: Optional message about the analysis
    """
    
    success: bool = Field(default=True)
    analysis: JobAnalysis
    message: Optional[str] = Field(
        default=None,
        description="Optional message about the analysis"
    )


class ResumeOptimizationRequest(BaseModel):
    """
    Request model for resume optimization.
    
    Attributes:
        user_id: ID of the user whose resume to optimize
        job_description: Job description to optimize against
        optimization_level: Level of optimization (basic, standard, advanced)
        include_suggestions: Whether to include content improvement suggestions
    """
    
    user_id: UUID = Field(..., description="User ID")
    job_description: str = Field(
        ...,
        min_length=50,
        max_length=10000,
        description="Target job description"
    )
    optimization_level: OptimizationLevel = Field(
        default=OptimizationLevel.STANDARD,
        description="Optimization depth level"
    )
    include_suggestions: bool = Field(
        default=True,
        description="Include detailed improvement suggestions"
    )


class ResumeOptimizationResponse(BaseModel):
    """
    Response model for resume optimization.
    
    Attributes:
        success: Whether optimization was successful
        optimization: Optimization results and suggestions
        job_match_score: Overall job match score (0-100)
        ats_score: ATS compatibility score (0-100)
        message: Optional message about the optimization
    """
    
    success: bool = Field(default=True)
    optimization: ResumeOptimization
    job_match_score: float = Field(..., ge=0, le=100)
    ats_score: float = Field(..., ge=0, le=100)
    message: Optional[str] = Field(default=None)


class KeywordExtractionRequest(BaseModel):
    """
    Request model for keyword extraction.
    
    Attributes:
        text: Text to extract keywords from
        max_keywords: Maximum number of keywords to extract
        category: Category of keywords to focus on
    """
    
    text: str = Field(
        ...,
        min_length=20,
        description="Text to extract keywords from"
    )
    max_keywords: int = Field(
        default=20,
        ge=5,
        le=50,
        description="Maximum keywords to extract"
    )
    category: Optional[str] = Field(
        default=None,
        description="Keyword category filter (e.g., 'technical', 'soft_skills')"
    )


class KeywordExtractionResponse(BaseModel):
    """
    Response model for keyword extraction.
    
    Attributes:
        success: Whether extraction was successful
        keywords: List of extracted keywords
        categorized_keywords: Keywords grouped by category
    """
    
    success: bool = Field(default=True)
    keywords: List[str] = Field(description="Extracted keywords")
    categorized_keywords: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Keywords grouped by category"
    )


class HealthCheckResponse(BaseModel):
    """
    Health check response for AI service.
    
    Attributes:
        service: Service name
        status: Service status
        circuit_breaker_state: Current circuit breaker state
    """
    
    service: str = Field(default="ai_optimization")
    status: str = Field(description="Service status")
    circuit_breaker_state: str = Field(description="Circuit breaker state")


# API Endpoints

@router.post(
    "/analyze-job",
    response_model=JobAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze job description",
    description="Parse and analyze a job description to extract requirements, skills, and keywords",
    responses={
        200: {"description": "Job description analyzed successfully"},
        400: {"description": "Invalid job description"},
        503: {"description": "AI service unavailable"},
    }
)
async def analyze_job_description(
    request: JobDescriptionRequest = Body(...),
    ai_service: AIService = Depends(get_ai_service)
) -> JobAnalysisResponse:
    """
    Analyze a job description to extract structured information.
    
    This endpoint uses AI to parse job descriptions and extract:
    - Job title and company information
    - Required and preferred skills
    - Experience requirements
    - Education requirements
    - Key responsibilities
    - ATS-optimized keywords
    
    Args:
        request: Job description analysis request
        ai_service: AI service dependency
    
    Returns:
        Structured job analysis data
    
    Raises:
        HTTPException: When job description is invalid or service fails
    """
    logger.info(
        "Analyzing job description",
        extra={
            "description_length": len(request.job_description),
            "extract_keywords": request.extract_keywords
        }
    )
    
    try:
        async with ai_service:
            # Analyze job description
            analysis = await ai_service.analyze_job_description(
                job_description=request.job_description
            )
            
            logger.info(
                "Job description analysis complete",
                extra={
                    "job_title": analysis.job_title,
                    "skills_count": len(analysis.skills),
                    "keywords_count": len(analysis.keywords)
                }
            )
            
            return JobAnalysisResponse(
                success=True,
                analysis=analysis,
                message=f"Successfully analyzed job posting for {analysis.job_title}"
            )
            
    except JobDescriptionInvalidError as exc:
        logger.warning(
            "Invalid job description provided",
            extra={"error": str(exc)}
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": exc.error_code.value,
                "message": exc.message,
                "details": exc.details
            }
        ) from exc
    
    except JobParsingError as exc:
        logger.error(
            "Failed to parse job description",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": exc.error_code.value,
                "message": exc.message,
                "details": exc.details
            }
        ) from exc
    
    except AIServiceException as exc:
        logger.error(
            "AI service error during job analysis",
            exc_info=True
        )
        raise HTTPException(
            status_code=exc.status_code,
            detail={
                "error_code": exc.error_code.value,
                "message": exc.message,
                "details": exc.details
            }
        ) from exc
    
    except Exception as exc:
        logger.error(
            "Unexpected error during job analysis",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "An unexpected error occurred during job analysis",
                "message": str(exc)
            }
        ) from exc


@router.post(
    "/optimize-resume",
    response_model=ResumeOptimizationResponse,
    status_code=status.HTTP_200_OK,
    summary="Optimize resume for job",
    description="Optimize user resume content against a specific job description",
    responses={
        200: {"description": "Resume optimized successfully"},
        400: {"description": "Invalid request or incomplete profile"},
        404: {"description": "User profile not found"},
        503: {"description": "AI service unavailable"},
    }
)
async def optimize_resume(
    request: ResumeOptimizationRequest = Body(...),
    ai_service: AIService = Depends(get_ai_service)
) -> ResumeOptimizationResponse:
    """
    Optimize resume content for a specific job description.
    
    This endpoint analyzes the user's profile against job requirements and provides:
    - Overall job match score
    - Skills gap analysis
    - Keyword suggestions for ATS optimization
    - Content improvement recommendations
    - Formatting suggestions
    - ATS compatibility score
    
    Args:
        request: Resume optimization request
        ai_service: AI service dependency
    
    Returns:
        Resume optimization results with suggestions
    
    Raises:
        HTTPException: When optimization fails or profile is incomplete
    """
    logger.info(
        "Optimizing resume",
        extra={
            "user_id": str(request.user_id),
            "optimization_level": request.optimization_level.value
        }
    )
    
    try:
        async with ai_service:
            # First, analyze the job description
            job_analysis = await ai_service.analyze_job_description(
                job_description=request.job_description
            )
            
            # Fetch user profile data from database services
            from app.services.profile_service import ProfileService
            from app.services.project_service import ProjectService
            from app.services import SupabaseService
            
            profile_service = ProfileService()
            project_service = ProjectService()
            supabase_service = SupabaseService()
            
            # Get profile data
            profile = profile_service.get_profile(request.user_id)
            if not profile:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile not found"
                )
            
            # Get user's projects
            projects = project_service.get_user_projects(request.user_id)
            
            # Get education, certifications, internships from Supabase
            education = supabase_service.client.table("education").select("*").eq("user_id", str(request.user_id)).execute()
            certifications = supabase_service.client.table("certifications").select("*").eq("user_id", str(request.user_id)).execute()
            internships = supabase_service.client.table("internships").select("*").eq("user_id", str(request.user_id)).execute()
            courses = supabase_service.client.table("courses").select("*").eq("user_id", str(request.user_id)).execute()
            
            # Construct comprehensive user profile
            user_profile: Dict[str, Any] = {
                "user_id": str(request.user_id),
                "full_name": profile.full_name,
                "current_title": profile.current_title,
                "bio": profile.bio,
                "experience_years": profile.experience_years,
                "skills": [tech["technology_name"] for project in projects for tech in project.technologies],
                "projects": [
                    {
                        "title": p.title,
                        "description": p.description,
                        "technologies": p.technologies,
                        "category": p.category,
                        "github_url": p.github_url,
                        "live_url": p.live_url,
                    }
                    for p in projects
                ],
                "education": education.data if education and education.data else [],
                "certifications": certifications.data if certifications and certifications.data else [],
                "internships": internships.data if internships and internships.data else [],
                "courses": courses.data if courses and courses.data else [],
                "linkedin_url": profile.linkedin_url,
                "github_url": profile.github_url,
            }
            
            # Optimize resume content
            optimization = await ai_service.optimize_resume_content(
                user_profile=user_profile,
                job_analysis=job_analysis,
                optimization_level=request.optimization_level
            )
            
            logger.info(
                "Resume optimization complete",
                extra={
                    "user_id": str(request.user_id),
                    "match_score": optimization.match_score,
                    "ats_score": optimization.ats_compatibility_score
                }
            )
            
            return ResumeOptimizationResponse(
                success=True,
                optimization=optimization,
                job_match_score=optimization.match_score,
                ats_score=optimization.ats_compatibility_score,
                message=f"Resume optimized for {job_analysis.job_title} position"
            )
            
    except ResumeOptimizationException as exc:
        logger.error(
            "Resume optimization failed",
            exc_info=True
        )
        raise HTTPException(
            status_code=exc.status_code,
            detail={
                "error_code": exc.error_code.value,
                "message": exc.message,
                "details": exc.details
            }
        ) from exc
    
    except AIServiceException as exc:
        logger.error(
            "AI service error during resume optimization",
            exc_info=True
        )
        raise HTTPException(
            status_code=exc.status_code,
            detail={
                "error_code": exc.error_code.value,
                "message": exc.message,
                "details": exc.details
            }
        ) from exc
    
    except Exception as exc:
        logger.error(
            "Unexpected error during resume optimization",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "An unexpected error occurred during resume optimization",
                "message": str(exc)
            }
        ) from exc


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="AI service health check",
    description="Check the health status of the AI optimization service"
)
async def health_check(
    ai_service: AIService = Depends(get_ai_service)
) -> HealthCheckResponse:
    """
    Check AI service health and circuit breaker status.
    
    Returns:
        Service health status and circuit breaker state
    """
    circuit_state = ai_service.circuit_breaker.state.value
    
    # Determine overall status
    if circuit_state == "open":
        service_status = "degraded"
    elif circuit_state == "half_open":
        service_status = "recovering"
    else:
        service_status = "healthy"
    
    return HealthCheckResponse(
        service="ai_optimization",
        status=service_status,
        circuit_breaker_state=circuit_state
    )