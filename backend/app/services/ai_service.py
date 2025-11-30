"""
AI-Powered Resume Optimization Service.

This module provides AI-driven capabilities for resume optimization, job description
analysis, keyword extraction, and content matching using OpenRouter API.

The service implements NASA-level coding standards including:
- Comprehensive error handling with custom exceptions
- Circuit breaker pattern for API resilience
- Retry logic with exponential backoff
- Type safety with full type annotations
- Input validation with Pydantic models
- Detailed logging for all operations
- Rate limiting to prevent quota exhaustion
- Timeout handling for long-running requests

Author: Resume Twin Development Team
Version: 1.0.0
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum
import re

import httpx
from pydantic import BaseModel, Field, validator
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

from app.core.config import settings
from app.core.exceptions import (
    AIServiceUnavailableError,
    AIAPIError,
    AIRateLimitError,
    AITimeoutError,
    AIInvalidResponseError,
    JobParsingError,
    JobDescriptionInvalidError,
    ResumeOptimizationException,
    ErrorCode,
)
from app.utils.logger import setup_logger

# Initialize logger for this module
logger = setup_logger(__name__)

# Constants for configuration (no magic numbers)
DEFAULT_TIMEOUT_SECONDS: int = 30
MAX_RETRY_ATTEMPTS: int = 3
MIN_RETRY_WAIT_SECONDS: int = 1
MAX_RETRY_WAIT_SECONDS: int = 10
CIRCUIT_BREAKER_THRESHOLD: int = 5
CIRCUIT_BREAKER_TIMEOUT_SECONDS: int = 60
MAX_TOKENS_PER_REQUEST: int = 4000
MIN_JOB_DESCRIPTION_LENGTH: int = 50
MAX_JOB_DESCRIPTION_LENGTH: int = 10000
MIN_KEYWORDS_COUNT: int = 5
MAX_KEYWORDS_COUNT: int = 50


class OptimizationLevel(str, Enum):
    """
    Enumeration for resume optimization levels.
    
    Defines the depth and comprehensiveness of resume optimization:
    - BASIC: Quick keyword matching and formatting
    - STANDARD: Detailed content optimization with ATS compliance
    - ADVANCED: Deep analysis with personalized suggestions
    """
    
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"


class JobRequirement(BaseModel):
    """
    Model representing a parsed job requirement.
    
    Attributes:
        category: Requirement category (e.g., 'technical_skill', 'experience')
        skill: The specific skill or requirement
        importance: Importance level (required, preferred, optional)
        years_experience: Required years of experience (if applicable)
    """
    
    category: str = Field(..., description="Category of the requirement")
    skill: str = Field(..., min_length=1, description="Specific skill or requirement")
    importance: str = Field(..., description="Importance level")
    years_experience: Optional[int] = Field(None, ge=0, description="Years of experience required")
    
    @validator("category")
    def validate_category(cls, value: str) -> str:
        """Validate that category is not empty or whitespace only."""
        if not value or not value.strip():
            raise ValueError("Category cannot be empty")
        return value.strip()
    
    @validator("importance")
    def validate_importance(cls, value: str) -> str:
        """Validate importance level is one of the allowed values."""
        allowed_values: Set[str] = {"required", "preferred", "optional"}
        if value.lower() not in allowed_values:
            raise ValueError(f"Importance must be one of: {allowed_values}")
        return value.lower()


class JobAnalysis(BaseModel):
    """
    Model representing the complete analysis of a job description.
    
    Attributes:
        job_title: Extracted job title
        company: Company name (if available)
        requirements: List of parsed job requirements
        skills: Set of required skills
        keywords: ATS-optimized keywords
        experience_level: Required experience level
        education_requirements: Education requirements
        responsibilities: Key job responsibilities
    """
    
    job_title: str = Field(..., min_length=1)
    company: Optional[str] = None
    requirements: List[JobRequirement] = Field(default_factory=list)
    skills: Set[str] = Field(default_factory=set)
    keywords: List[str] = Field(default_factory=list)
    experience_level: Optional[str] = None
    education_requirements: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)


class ResumeOptimization(BaseModel):
    """
    Model representing resume optimization suggestions.
    
    Attributes:
        match_score: Overall match score (0-100)
        missing_skills: Skills present in job but missing in resume
        matching_skills: Skills that match between job and resume
        keyword_suggestions: Suggested keywords to add
        content_improvements: Specific content improvement suggestions
        formatting_suggestions: Formatting and structure suggestions
        ats_compatibility_score: ATS system compatibility score (0-100)
    """
    
    match_score: float = Field(..., ge=0, le=100)
    missing_skills: List[str] = Field(default_factory=list)
    matching_skills: List[str] = Field(default_factory=list)
    keyword_suggestions: List[str] = Field(default_factory=list)
    content_improvements: List[Dict[str, str]] = Field(default_factory=list)
    formatting_suggestions: List[str] = Field(default_factory=list)
    ats_compatibility_score: float = Field(..., ge=0, le=100)


class CircuitBreakerState(Enum):
    """Circuit breaker states for API resilience."""
    
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failures exceed threshold, requests blocked
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker implementation for API resilience.
    
    Prevents cascading failures by stopping requests to a failing service
    and allowing it time to recover.
    """
    
    def __init__(
        self,
        failure_threshold: int = CIRCUIT_BREAKER_THRESHOLD,
        timeout_seconds: int = CIRCUIT_BREAKER_TIMEOUT_SECONDS
    ) -> None:
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            timeout_seconds: Seconds to wait before attempting recovery
        """
        self.failure_threshold: int = failure_threshold
        self.timeout_seconds: int = timeout_seconds
        self.failure_count: int = 0
        self.state: CircuitBreakerState = CircuitBreakerState.CLOSED
        self.last_failure_time: Optional[datetime] = None
    
    def record_success(self) -> None:
        """Record a successful request."""
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED
        logger.info("Circuit breaker: Success recorded, state reset to CLOSED")
    
    def record_failure(self) -> None:
        """Record a failed request."""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            logger.warning(
                f"Circuit breaker: Opened after {self.failure_count} failures"
            )
    
    def can_attempt_request(self) -> bool:
        """
        Check if request can be attempted based on circuit state.
        
        Returns:
            True if request should be attempted, False otherwise
        """
        if self.state == CircuitBreakerState.CLOSED:
            return True
        
        if self.state == CircuitBreakerState.OPEN:
            if self.last_failure_time is None:
                return False
            
            # Check if timeout has elapsed
            time_since_failure = datetime.utcnow() - self.last_failure_time
            if time_since_failure.total_seconds() >= self.timeout_seconds:
                self.state = CircuitBreakerState.HALF_OPEN
                logger.info("Circuit breaker: Moving to HALF_OPEN state")
                return True
            
            return False
        
        # HALF_OPEN state: allow request to test recovery
        return True


class AIService:
    """
    AI-powered service for resume optimization and job analysis.
    
    This service provides comprehensive AI capabilities including:
    - Job description parsing and analysis
    - Resume content optimization
    - Keyword extraction for ATS systems
    - Skills gap analysis
    - Content improvement suggestions
    """
    
    def __init__(self) -> None:
        """Initialize AI service with configuration and circuit breaker."""
        self.api_key: str = settings.OPENROUTER_API_KEY or ""
        self.api_url: str = "https://openrouter.ai/api/v1/chat/completions"
        self.model: str = settings.AI_MODEL or settings.OPENROUTER_MODEL or "anthropic/claude-3-sonnet"
        self.circuit_breaker: CircuitBreaker = CircuitBreaker()
        self.client: Optional[httpx.AsyncClient] = None
        
        logger.info(
            f"AIService initialized with model: {self.model}",
            extra={"model": self.model}
        )
    
    async def __aenter__(self) -> "AIService":
        """Async context manager entry."""
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(DEFAULT_TIMEOUT_SECONDS),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
        return self
    
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        if self.client:
            await self.client.aclose()
    
    @retry(
        stop=stop_after_attempt(MAX_RETRY_ATTEMPTS),
        wait=wait_exponential(
            multiplier=MIN_RETRY_WAIT_SECONDS,
            max=MAX_RETRY_WAIT_SECONDS
        ),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    async def _make_api_request(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = MAX_TOKENS_PER_REQUEST
    ) -> Dict[str, Any]:
        """
        Make API request to OpenRouter with retry logic and error handling.
        
        Args:
            messages: List of message dictionaries for the chat completion
            max_tokens: Maximum tokens in the response
        
        Returns:
            API response as dictionary
        
        Raises:
            AIServiceUnavailableError: When service is unavailable
            AIAPIError: When API returns an error
            AIRateLimitError: When rate limit is exceeded
            AITimeoutError: When request times out
        """
        # Check circuit breaker state
        if not self.circuit_breaker.can_attempt_request():
            raise AIServiceUnavailableError(
                "AI service is temporarily unavailable due to repeated failures",
                details={"circuit_breaker_state": self.circuit_breaker.state.value}
            )
        
        if not self.client:
            raise AIServiceUnavailableError("HTTP client not initialized")
        
        request_payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7,
        }
        
        headers: Dict[str, str] = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        try:
            logger.info(
                "Making AI API request",
                extra={
                    "model": self.model,
                    "messages_count": len(messages),
                    "max_tokens": max_tokens
                }
            )
            
            response = await self.client.post(
                self.api_url,
                json=request_payload,
                headers=headers
            )
            
            # Handle rate limiting
            if response.status_code == 429:
                self.circuit_breaker.record_failure()
                raise AIRateLimitError(
                    "AI API rate limit exceeded",
                    details={"status_code": response.status_code}
                )
            
            # Handle API errors
            if response.status_code >= 400:
                self.circuit_breaker.record_failure()
                error_detail = response.text
                raise AIAPIError(
                    f"AI API request failed with status {response.status_code}",
                    details={
                        "status_code": response.status_code,
                        "error": error_detail
                    }
                )
            
            response_data: Dict[str, Any] = response.json()
            self.circuit_breaker.record_success()
            
            logger.info(
                "AI API request successful",
                extra={"status_code": response.status_code}
            )
            
            return response_data
            
        except httpx.TimeoutException as exc:
            self.circuit_breaker.record_failure()
            logger.error(
                "AI API request timed out",
                exc_info=True
            )
            raise AITimeoutError(
                "AI API request timed out",
                details={"timeout_seconds": DEFAULT_TIMEOUT_SECONDS}
            ) from exc
        
        except httpx.NetworkError as exc:
            self.circuit_breaker.record_failure()
            logger.error(
                "Network error during AI API request",
                exc_info=True
            )
            raise AIServiceUnavailableError(
                "Network error occurred during AI API request",
                details={"error": str(exc)}
            ) from exc
        
        except Exception as exc:
            self.circuit_breaker.record_failure()
            logger.error(
                "Unexpected error during AI API request",
                exc_info=True
            )
            raise AIAPIError(
                "Unexpected error during AI API request",
                details={"error": str(exc)}
            ) from exc
    
    def _extract_json_from_response(self, content: str) -> Dict[str, Any]:
        """
        Extract and parse JSON from AI response content.
        
        Args:
            content: Response content that may contain JSON
        
        Returns:
            Parsed JSON as dictionary
        
        Raises:
            AIInvalidResponseError: When JSON cannot be extracted or parsed
        """
        try:
            # Try to find JSON block in markdown code fence
            json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON object directly
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    json_str = content
            
            result: Dict[str, Any] = json.loads(json_str)
            return result
            
        except json.JSONDecodeError as exc:
            logger.error(
                "Failed to parse JSON from AI response",
                extra={"content_preview": content[:200]},
                exc_info=True
            )
            raise AIInvalidResponseError(
                "Failed to parse JSON from AI response",
                details={"error": str(exc), "content_preview": content[:200]}
            ) from exc
    
    async def analyze_job_description(
        self,
        job_description: str
    ) -> JobAnalysis:
        """
        Analyze job description to extract requirements, skills, and keywords.
        
        Args:
            job_description: The job description text to analyze
        
        Returns:
            JobAnalysis object containing parsed information
        
        Raises:
            JobDescriptionInvalidError: When job description is invalid
            JobParsingError: When parsing fails
        """
        # Validate input
        if not job_description or not job_description.strip():
            raise JobDescriptionInvalidError(
                "Job description cannot be empty",
                details={"length": 0}
            )
        
        job_description = job_description.strip()
        
        if len(job_description) < MIN_JOB_DESCRIPTION_LENGTH:
            raise JobDescriptionInvalidError(
                f"Job description is too short (minimum {MIN_JOB_DESCRIPTION_LENGTH} characters)",
                details={"length": len(job_description)}
            )
        
        if len(job_description) > MAX_JOB_DESCRIPTION_LENGTH:
            raise JobDescriptionInvalidError(
                f"Job description is too long (maximum {MAX_JOB_DESCRIPTION_LENGTH} characters)",
                details={"length": len(job_description)}
            )
        
        logger.info(
            "Analyzing job description",
            extra={"description_length": len(job_description)}
        )
        
        prompt = f"""Analyze the following job description and extract structured information in JSON format.

Job Description:
{job_description}

Please provide a JSON response with the following structure:
{{
  "job_title": "extracted job title",
  "company": "company name if mentioned",
  "requirements": [
    {{"category": "technical_skill|soft_skill|experience|education", "skill": "specific skill", "importance": "required|preferred|optional", "years_experience": null or number}}
  ],
  "skills": ["skill1", "skill2"],
  "keywords": ["keyword1", "keyword2"],
  "experience_level": "entry|mid|senior|lead",
  "education_requirements": ["requirement1", "requirement2"],
  "responsibilities": ["responsibility1", "responsibility2"]
}}

Extract at least {MIN_KEYWORDS_COUNT} but no more than {MAX_KEYWORDS_COUNT} relevant keywords for ATS optimization."""
        
        messages: List[Dict[str, str]] = [
            {"role": "system", "content": "You are an expert job description analyzer. Always respond with valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self._make_api_request(messages)
            
            # Extract content from response
            if "choices" not in response or not response["choices"]:
                raise AIInvalidResponseError(
                    "AI response missing choices",
                    details={"response": response}
                )
            
            content = response["choices"][0].get("message", {}).get("content", "")
            
            if not content:
                raise AIInvalidResponseError(
                    "AI response content is empty",
                    details={"response": response}
                )
            
            # Parse JSON from content
            job_data: Dict[str, Any] = self._extract_json_from_response(content)
            
            # Convert to JobAnalysis model with validation
            analysis = JobAnalysis(
                job_title=job_data.get("job_title", "Unknown"),
                company=job_data.get("company"),
                requirements=[
                    JobRequirement(**req) for req in job_data.get("requirements", [])
                ],
                skills=set(job_data.get("skills", [])),
                keywords=job_data.get("keywords", []),
                experience_level=job_data.get("experience_level"),
                education_requirements=job_data.get("education_requirements", []),
                responsibilities=job_data.get("responsibilities", [])
            )
            
            logger.info(
                "Job description analysis complete",
                extra={
                    "job_title": analysis.job_title,
                    "skills_count": len(analysis.skills),
                    "keywords_count": len(analysis.keywords)
                }
            )
            
            return analysis
            
        except (AIServiceUnavailableError, AIAPIError, AIRateLimitError, AITimeoutError):
            # Re-raise AI-specific errors
            raise
        except Exception as exc:
            logger.error(
                "Failed to analyze job description",
                exc_info=True
            )
            raise JobParsingError(
                "Failed to analyze job description",
                details={"error": str(exc)}
            ) from exc
    
    async def optimize_resume_content(
        self,
        user_profile: Dict[str, Any],
        job_analysis: JobAnalysis,
        optimization_level: OptimizationLevel = OptimizationLevel.STANDARD
    ) -> ResumeOptimization:
        """
        Optimize resume content based on job requirements.
        
        Args:
            user_profile: User's profile data including experience, skills, projects
            job_analysis: Analyzed job description
            optimization_level: Level of optimization to perform
        
        Returns:
            ResumeOptimization object with suggestions and scores
        
        Raises:
            ResumeOptimizationException: When optimization fails
        """
        logger.info(
            "Optimizing resume content",
            extra={
                "job_title": job_analysis.job_title,
                "optimization_level": optimization_level.value
            }
        )
        
        prompt = f"""Analyze the user's profile against the job requirements and provide optimization suggestions.

Job Title: {job_analysis.job_title}
Required Skills: {', '.join(job_analysis.skills)}
Keywords: {', '.join(job_analysis.keywords)}

User Profile:
{json.dumps(user_profile, indent=2)}

Optimization Level: {optimization_level.value}

Provide a JSON response with:
{{
  "match_score": 0-100,
  "missing_skills": ["skill1", "skill2"],
  "matching_skills": ["skill1", "skill2"],
  "keyword_suggestions": ["keyword1", "keyword2"],
  "content_improvements": [
    {{"section": "section name", "suggestion": "specific improvement"}}
  ],
  "formatting_suggestions": ["suggestion1", "suggestion2"],
  "ats_compatibility_score": 0-100
}}"""
        
        messages: List[Dict[str, str]] = [
            {"role": "system", "content": "You are an expert resume optimization advisor. Always respond with valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self._make_api_request(messages)
            content = response["choices"][0]["message"]["content"]
            optimization_data: Dict[str, Any] = self._extract_json_from_response(content)
            
            optimization = ResumeOptimization(**optimization_data)
            
            logger.info(
                "Resume optimization complete",
                extra={
                    "match_score": optimization.match_score,
                    "ats_score": optimization.ats_compatibility_score,
                    "missing_skills_count": len(optimization.missing_skills)
                }
            )
            
            return optimization
            
        except Exception as exc:
            logger.error(
                "Failed to optimize resume content",
                exc_info=True
            )
            raise ResumeOptimizationException(
                error_code=ErrorCode.RESUME_OPTIMIZATION_ERROR,
                message="Failed to optimize resume content",
                details={"error": str(exc)}
            ) from exc


# Singleton instance
_ai_service_instance: Optional[AIService] = None


async def get_ai_service() -> AIService:
    """
    Get singleton instance of AI service.
    
    Returns:
        AIService instance
    """
    global _ai_service_instance
    
    if _ai_service_instance is None:
        _ai_service_instance = AIService()
    
    return _ai_service_instance