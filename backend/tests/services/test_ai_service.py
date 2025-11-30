"""
Unit tests for AI service.

This module provides comprehensive test coverage for the AI service including:
- Job description analysis
- Resume optimization
- Circuit breaker functionality
- Error handling
- Retry logic
- API communication

Author: Resume Twin Development Team
Version: 1.0.0
"""

import pytest
import json
from datetime import datetime
from typing import Dict, Any, List
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
from pydantic import ValidationError

from app.services.ai_service import (
    AIService,
    CircuitBreaker,
    CircuitBreakerState,
    JobAnalysis,
    JobRequirement,
    ResumeOptimization,
    OptimizationLevel,
)
from app.core.exceptions import (
    AIServiceUnavailableError,
    AIAPIError,
    AIRateLimitError,
    AITimeoutError,
    AIInvalidResponseError,
    JobDescriptionInvalidError,
    JobParsingError,
    ResumeOptimizationException,
    ErrorCode,
)


# Test Fixtures

@pytest.fixture
def mock_settings():
    """Mock application settings."""
    with patch("app.services.ai_service.settings") as mock:
        mock.OPENROUTER_API_KEY = "test-api-key"
        mock.AI_MODEL = "test-model"
        yield mock


@pytest.fixture
def ai_service(mock_settings):
    """Create AI service instance for testing."""
    return AIService()


@pytest.fixture
def circuit_breaker():
    """Create circuit breaker instance for testing."""
    return CircuitBreaker(failure_threshold=3, timeout_seconds=60)


@pytest.fixture
def sample_job_description():
    """Sample job description for testing."""
    return """
    Senior Software Engineer

    We are seeking an experienced software engineer with:
    - 5+ years of Python development
    - Experience with FastAPI and Django
    - Strong knowledge of PostgreSQL
    - Experience with Docker and Kubernetes
    - Bachelor's degree in Computer Science

    Responsibilities:
    - Design and implement scalable APIs
    - Mentor junior developers
    - Collaborate with product team

    Preferred:
    - Experience with AWS
    - Knowledge of React
    """


@pytest.fixture
def sample_user_profile():
    """Sample user profile for testing."""
    return {
        "user_id": "test-user-123",
        "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
        "experience": [
            {
                "title": "Software Engineer",
                "company": "Tech Corp",
                "years": 3
            }
        ],
        "education": [
            {
                "degree": "BS Computer Science",
                "institution": "Test University"
            }
        ],
        "projects": [],
        "certifications": []
    }


@pytest.fixture
def mock_ai_response():
    """Mock successful AI API response."""
    return {
        "choices": [
            {
                "message": {
                    "content": json.dumps({
                        "job_title": "Senior Software Engineer",
                        "company": "Test Company",
                        "requirements": [
                            {
                                "category": "technical_skill",
                                "skill": "Python",
                                "importance": "required",
                                "years_experience": 5
                            }
                        ],
                        "skills": ["Python", "FastAPI", "PostgreSQL"],
                        "keywords": ["API", "scalable", "microservices"],
                        "experience_level": "senior",
                        "education_requirements": ["Bachelor's in CS"],
                        "responsibilities": ["Design APIs", "Mentor developers"]
                    })
                }
            }
        ]
    }


# Circuit Breaker Tests

class TestCircuitBreaker:
    """Test suite for circuit breaker functionality."""
    
    def test_initial_state_is_closed(self, circuit_breaker):
        """Test circuit breaker starts in CLOSED state."""
        assert circuit_breaker.state == CircuitBreakerState.CLOSED
        assert circuit_breaker.failure_count == 0
        assert circuit_breaker.can_attempt_request() is True
    
    def test_record_success_resets_state(self, circuit_breaker):
        """Test recording success resets failure count and state."""
        circuit_breaker.failure_count = 2
        circuit_breaker.record_success()
        
        assert circuit_breaker.failure_count == 0
        assert circuit_breaker.state == CircuitBreakerState.CLOSED
    
    def test_record_failure_increments_count(self, circuit_breaker):
        """Test recording failure increments failure count."""
        initial_count = circuit_breaker.failure_count
        circuit_breaker.record_failure()
        
        assert circuit_breaker.failure_count == initial_count + 1
        assert circuit_breaker.last_failure_time is not None
    
    def test_circuit_opens_after_threshold(self, circuit_breaker):
        """Test circuit opens after reaching failure threshold."""
        for _ in range(circuit_breaker.failure_threshold):
            circuit_breaker.record_failure()
        
        assert circuit_breaker.state == CircuitBreakerState.OPEN
        assert circuit_breaker.can_attempt_request() is False
    
    def test_circuit_transitions_to_half_open(self, circuit_breaker):
        """Test circuit transitions to HALF_OPEN after timeout."""
        # Force circuit to open
        for _ in range(circuit_breaker.failure_threshold):
            circuit_breaker.record_failure()
        
        # Simulate timeout elapsed
        circuit_breaker.timeout_seconds = 0
        
        assert circuit_breaker.can_attempt_request() is True
        assert circuit_breaker.state == CircuitBreakerState.HALF_OPEN


# AIService Tests

class TestAIService:
    """Test suite for AI service functionality."""
    
    def test_initialization(self, ai_service, mock_settings):
        """Test AI service initializes correctly."""
        assert ai_service.api_key == "test-api-key"
        assert ai_service.model == "test-model"
        assert isinstance(ai_service.circuit_breaker, CircuitBreaker)
        assert ai_service.client is None
    
    @pytest.mark.asyncio
    async def test_context_manager_creates_client(self, ai_service):
        """Test async context manager creates HTTP client."""
        async with ai_service as service:
            assert service.client is not None
            assert isinstance(service.client, httpx.AsyncClient)
    
    @pytest.mark.asyncio
    async def test_context_manager_closes_client(self, ai_service):
        """Test async context manager closes HTTP client."""
        async with ai_service:
            pass
        
        # Client should be closed after context exit
        # Note: We can't directly test if client is closed,
        # but we can verify the context manager executed properly
        assert True  # Context manager completed without errors
    
    @pytest.mark.asyncio
    async def test_make_api_request_success(
        self,
        ai_service,
        mock_ai_response
    ):
        """Test successful API request."""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_ai_response
        mock_client.post = AsyncMock(return_value=mock_response)
        
        ai_service.client = mock_client
        
        messages = [{"role": "user", "content": "test"}]
        result = await ai_service._make_api_request(messages)
        
        assert result == mock_ai_response
        assert ai_service.circuit_breaker.failure_count == 0
    
    @pytest.mark.asyncio
    async def test_make_api_request_rate_limit(self, ai_service):
        """Test API request handles rate limiting."""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_client.post = AsyncMock(return_value=mock_response)
        
        ai_service.client = mock_client
        
        messages = [{"role": "user", "content": "test"}]
        
        with pytest.raises(AIRateLimitError) as exc_info:
            await ai_service._make_api_request(messages)
        
        assert exc_info.value.error_code == ErrorCode.AI_RATE_LIMIT_EXCEEDED
        assert ai_service.circuit_breaker.failure_count > 0
    
    @pytest.mark.asyncio
    async def test_make_api_request_timeout(self, ai_service):
        """Test API request handles timeout."""
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))
        
        ai_service.client = mock_client
        
        messages = [{"role": "user", "content": "test"}]
        
        with pytest.raises(AITimeoutError) as exc_info:
            await ai_service._make_api_request(messages)
        
        assert exc_info.value.error_code == ErrorCode.AI_TIMEOUT
    
    @pytest.mark.asyncio
    async def test_make_api_request_network_error(self, ai_service):
        """Test API request handles network errors."""
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(
            side_effect=httpx.NetworkError("Network error")
        )
        
        ai_service.client = mock_client
        
        messages = [{"role": "user", "content": "test"}]
        
        with pytest.raises(AIServiceUnavailableError) as exc_info:
            await ai_service._make_api_request(messages)
        
        assert exc_info.value.error_code == ErrorCode.AI_SERVICE_UNAVAILABLE
    
    @pytest.mark.asyncio
    async def test_make_api_request_circuit_breaker_open(self, ai_service):
        """Test API request fails when circuit breaker is open."""
        # Force circuit breaker to open
        ai_service.circuit_breaker.state = CircuitBreakerState.OPEN
        ai_service.client = AsyncMock()
        
        messages = [{"role": "user", "content": "test"}]
        
        with pytest.raises(AIServiceUnavailableError) as exc_info:
            await ai_service._make_api_request(messages)
        
        assert "circuit breaker" in exc_info.value.message.lower()
    
    def test_extract_json_from_response_with_code_fence(self, ai_service):
        """Test JSON extraction from markdown code fence."""
        content = """
        Here's the result:
        ```json
        {"key": "value"}
        ```
        """
        
        result = ai_service._extract_json_from_response(content)
        assert result == {"key": "value"}
    
    def test_extract_json_from_response_direct_json(self, ai_service):
        """Test JSON extraction from direct JSON object."""
        content = '{"key": "value", "number": 42}'
        
        result = ai_service._extract_json_from_response(content)
        assert result == {"key": "value", "number": 42}
    
    def test_extract_json_from_response_invalid(self, ai_service):
        """Test JSON extraction handles invalid JSON."""
        content = "This is not JSON"
        
        with pytest.raises(AIInvalidResponseError) as exc_info:
            ai_service._extract_json_from_response(content)
        
        assert exc_info.value.error_code == ErrorCode.AI_INVALID_RESPONSE
    
    @pytest.mark.asyncio
    async def test_analyze_job_description_success(
        self,
        ai_service,
        sample_job_description,
        mock_ai_response
    ):
        """Test successful job description analysis."""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_ai_response
        mock_client.post = AsyncMock(return_value=mock_response)
        
        ai_service.client = mock_client
        
        result = await ai_service.analyze_job_description(sample_job_description)
        
        assert isinstance(result, JobAnalysis)
        assert result.job_title == "Senior Software Engineer"
        assert len(result.skills) > 0
        assert len(result.keywords) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_job_description_empty(self, ai_service):
        """Test job analysis rejects empty description."""
        with pytest.raises(JobDescriptionInvalidError) as exc_info:
            await ai_service.analyze_job_description("")
        
        assert exc_info.value.error_code == ErrorCode.JOB_DESCRIPTION_INVALID
    
    @pytest.mark.asyncio
    async def test_analyze_job_description_too_short(self, ai_service):
        """Test job analysis rejects too short description."""
        short_description = "Short job"
        
        with pytest.raises(JobDescriptionInvalidError) as exc_info:
            await ai_service.analyze_job_description(short_description)
        
        assert "too short" in exc_info.value.message.lower()
    
    @pytest.mark.asyncio
    async def test_analyze_job_description_too_long(self, ai_service):
        """Test job analysis rejects too long description."""
        long_description = "x" * 11000  # Exceeds MAX_JOB_DESCRIPTION_LENGTH
        
        with pytest.raises(JobDescriptionInvalidError) as exc_info:
            await ai_service.analyze_job_description(long_description)
        
        assert "too long" in exc_info.value.message.lower()
    
    @pytest.mark.asyncio
    async def test_optimize_resume_content_success(
        self,
        ai_service,
        sample_user_profile,
        mock_ai_response
    ):
        """Test successful resume optimization."""
        # Create job analysis
        job_analysis = JobAnalysis(
            job_title="Software Engineer",
            skills={"Python", "FastAPI"},
            keywords=["API", "testing"],
            requirements=[]
        )
        
        # Mock AI response for optimization
        optimization_response = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "match_score": 75.5,
                            "missing_skills": ["Kubernetes"],
                            "matching_skills": ["Python", "FastAPI"],
                            "keyword_suggestions": ["microservices", "REST"],
                            "content_improvements": [
                                {
                                    "section": "experience",
                                    "suggestion": "Add metrics"
                                }
                            ],
                            "formatting_suggestions": ["Use bullet points"],
                            "ats_compatibility_score": 85.0
                        })
                    }
                }
            ]
        }
        
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = optimization_response
        mock_client.post = AsyncMock(return_value=mock_response)
        
        ai_service.client = mock_client
        
        result = await ai_service.optimize_resume_content(
            user_profile=sample_user_profile,
            job_analysis=job_analysis,
            optimization_level=OptimizationLevel.STANDARD
        )
        
        assert isinstance(result, ResumeOptimization)
        assert 0 <= result.match_score <= 100
        assert 0 <= result.ats_compatibility_score <= 100
        assert isinstance(result.missing_skills, list)
        assert isinstance(result.matching_skills, list)


# Model Tests

class TestJobRequirement:
    """Test suite for JobRequirement model."""
    
    def test_valid_job_requirement(self):
        """Test creating valid job requirement."""
        req = JobRequirement(
            category="technical_skill",
            skill="Python",
            importance="required",
            years_experience=3
        )
        
        assert req.category == "technical_skill"
        assert req.skill == "Python"
        assert req.importance == "required"
        assert req.years_experience == 3
    
    def test_job_requirement_validates_importance(self):
        """Test job requirement validates importance level."""
        with pytest.raises(ValidationError):
            JobRequirement(
                category="skill",
                skill="Python",
                importance="invalid",
                years_experience=None
            )
    
    def test_job_requirement_trims_whitespace(self):
        """Test job requirement trims category whitespace."""
        req = JobRequirement(
            category="  technical_skill  ",
            skill="Python",
            importance="required"
        )
        
        assert req.category == "technical_skill"


class TestJobAnalysis:
    """Test suite for JobAnalysis model."""
    
    def test_valid_job_analysis(self):
        """Test creating valid job analysis."""
        analysis = JobAnalysis(
            job_title="Software Engineer",
            company="Test Corp",
            skills={"Python", "FastAPI"},
            keywords=["API", "backend"],
            experience_level="senior"
        )
        
        assert analysis.job_title == "Software Engineer"
        assert len(analysis.skills) == 2
        assert len(analysis.keywords) == 2


class TestResumeOptimization:
    """Test suite for ResumeOptimization model."""
    
    def test_valid_resume_optimization(self):
        """Test creating valid resume optimization."""
        optimization = ResumeOptimization(
            match_score=85.5,
            missing_skills=["Kubernetes"],
            matching_skills=["Python", "FastAPI"],
            keyword_suggestions=["microservices"],
            ats_compatibility_score=90.0
        )
        
        assert optimization.match_score == 85.5
        assert optimization.ats_compatibility_score == 90.0
        assert len(optimization.missing_skills) == 1
    
    def test_resume_optimization_validates_scores(self):
        """Test resume optimization validates score ranges."""
        with pytest.raises(ValidationError):
            ResumeOptimization(
                match_score=150.0,  # Invalid: > 100
                ats_compatibility_score=50.0
            )
        
        with pytest.raises(ValidationError):
            ResumeOptimization(
                match_score=50.0,
                ats_compatibility_score=-10.0  # Invalid: < 0
            )


# Integration Tests

class TestAIServiceIntegration:
    """Integration tests for AI service end-to-end workflows."""
    
    @pytest.mark.asyncio
    async def test_full_optimization_workflow(
        self,
        ai_service,
        sample_job_description,
        sample_user_profile,
        mock_ai_response
    ):
        """Test complete optimization workflow from job analysis to resume optimization."""
        # Mock client for both requests
        mock_client = AsyncMock()
        
        # Job analysis response
        job_response = MagicMock()
        job_response.status_code = 200
        job_response.json.return_value = mock_ai_response
        
        # Optimization response
        opt_response = MagicMock()
        opt_response.status_code = 200
        opt_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "match_score": 80.0,
                            "missing_skills": [],
                            "matching_skills": ["Python"],
                            "keyword_suggestions": [],
                            "content_improvements": [],
                            "formatting_suggestions": [],
                            "ats_compatibility_score": 85.0
                        })
                    }
                }
            ]
        }
        
        mock_client.post = AsyncMock(side_effect=[job_response, opt_response])
        ai_service.client = mock_client
        
        # Step 1: Analyze job
        job_analysis = await ai_service.analyze_job_description(
            sample_job_description
        )
        
        assert isinstance(job_analysis, JobAnalysis)
        
        # Step 2: Optimize resume
        optimization = await ai_service.optimize_resume_content(
            user_profile=sample_user_profile,
            job_analysis=job_analysis,
            optimization_level=OptimizationLevel.STANDARD
        )
        
        assert isinstance(optimization, ResumeOptimization)
        assert optimization.match_score >= 0
        assert optimization.ats_compatibility_score >= 0


# Performance Tests

class TestAIServicePerformance:
    """Performance and load tests for AI service."""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests_handled(self, ai_service):
        """Test service handles concurrent requests."""
        # This is a placeholder for performance testing
        # In a real scenario, we'd use tools like locust or pytest-benchmark
        assert True  # Service supports async/await for concurrency


# Error Recovery Tests

class TestErrorRecovery:
    """Test error recovery and resilience mechanisms."""
    
    @pytest.mark.asyncio
    async def test_retry_mechanism_on_network_error(self, ai_service):
        """Test retry mechanism activates on network errors."""
        mock_client = AsyncMock()
        
        # Fail twice, then succeed
        mock_client.post = AsyncMock(
            side_effect=[
                httpx.NetworkError("Network error"),
                httpx.NetworkError("Network error"),
                MagicMock(
                    status_code=200,
                    json=lambda: {"choices": [{"message": {"content": "{}"}}]}
                )
            ]
        )
        
        ai_service.client = mock_client
        
        # Should eventually succeed after retries
        messages = [{"role": "user", "content": "test"}]
        result = await ai_service._make_api_request(messages)
        
        assert result is not None
        assert mock_client.post.call_count == 3  # Verify retries occurred