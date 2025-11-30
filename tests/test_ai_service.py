"""
Unit Tests for AI Service.

Tests cover:
- Job description analysis
- Resume optimization
- Circuit breaker functionality
- API error handling
- Input validation
- JSON extraction from responses
"""

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime
import json
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from app.services.ai_service import (
    AIService,
    CircuitBreaker,
    CircuitBreakerState,
    OptimizationLevel,
    JobRequirement,
    JobAnalysis,
    ResumeOptimization,
    get_ai_service,
    MIN_JOB_DESCRIPTION_LENGTH,
    MAX_JOB_DESCRIPTION_LENGTH,
)
from app.core.exceptions import (
    AIServiceUnavailableError,
    AIAPIError,
    AIRateLimitError,
    AITimeoutError,
    AIInvalidResponseError,
    JobDescriptionInvalidError,
    JobParsingError
)


# ============================================================================
# Circuit Breaker Tests
# ============================================================================

class TestCircuitBreaker:
    """Tests for CircuitBreaker class."""
    
    def test_initial_state_is_closed(self):
        """Circuit breaker should start in closed state."""
        cb = CircuitBreaker()
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0
    
    def test_record_success_resets_failure_count(self):
        """Recording success should reset failure count."""
        cb = CircuitBreaker(failure_threshold=3)
        cb.failure_count = 2
        cb.record_success()
        assert cb.failure_count == 0
        assert cb.state == CircuitBreakerState.CLOSED
    
    def test_record_failure_increments_count(self):
        """Recording failure should increment failure count."""
        cb = CircuitBreaker(failure_threshold=5)
        cb.record_failure()
        assert cb.failure_count == 1
        assert cb.state == CircuitBreakerState.CLOSED
    
    def test_circuit_opens_after_threshold(self):
        """Circuit should open after reaching failure threshold."""
        cb = CircuitBreaker(failure_threshold=3)
        for _ in range(3):
            cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN
        assert cb.failure_count == 3
    
    def test_closed_circuit_allows_requests(self):
        """Closed circuit should allow requests."""
        cb = CircuitBreaker()
        assert cb.can_attempt_request() is True
    
    def test_open_circuit_blocks_requests(self):
        """Open circuit should block requests."""
        cb = CircuitBreaker(failure_threshold=1, timeout_seconds=60)
        cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN
        assert cb.can_attempt_request() is False
    
    def test_circuit_transitions_to_half_open_after_timeout(self):
        """Circuit should transition to half-open after timeout."""
        cb = CircuitBreaker(failure_threshold=1, timeout_seconds=0)
        cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN
        # Timeout of 0 means it should immediately allow half-open
        assert cb.can_attempt_request() is True
        assert cb.state == CircuitBreakerState.HALF_OPEN


# ============================================================================
# Model Validation Tests
# ============================================================================

class TestJobRequirement:
    """Tests for JobRequirement model validation."""
    
    def test_valid_job_requirement(self):
        """Should create valid job requirement."""
        req = JobRequirement(
            category="technical_skill",
            skill="Python",
            importance="required"
        )
        assert req.skill == "Python"
        assert req.importance == "required"
    
    def test_importance_normalization(self):
        """Should normalize importance to lowercase."""
        req = JobRequirement(
            category="technical_skill",
            skill="Python",
            importance="REQUIRED"
        )
        assert req.importance == "required"
    
    def test_invalid_importance_raises_error(self):
        """Should raise error for invalid importance level."""
        with pytest.raises(ValueError):
            JobRequirement(
                category="technical_skill",
                skill="Python",
                importance="mandatory"  # Not in allowed values
            )
    
    def test_empty_category_raises_error(self):
        """Should raise error for empty category."""
        with pytest.raises(ValueError):
            JobRequirement(
                category="   ",
                skill="Python",
                importance="required"
            )
    
    def test_optional_years_experience(self):
        """Years experience should be optional."""
        req = JobRequirement(
            category="experience",
            skill="Project Management",
            importance="preferred",
            years_experience=5
        )
        assert req.years_experience == 5


class TestJobAnalysis:
    """Tests for JobAnalysis model."""
    
    def test_create_job_analysis(self):
        """Should create valid job analysis."""
        analysis = JobAnalysis(
            job_title="Software Engineer",
            company="TechCorp",
            skills={"Python", "JavaScript"}
        )
        assert analysis.job_title == "Software Engineer"
        assert "Python" in analysis.skills
    
    def test_default_empty_collections(self):
        """Should have empty collections by default."""
        analysis = JobAnalysis(job_title="Engineer")
        assert analysis.requirements == []
        assert analysis.skills == set()
        assert analysis.keywords == []


class TestResumeOptimization:
    """Tests for ResumeOptimization model."""
    
    def test_score_validation(self):
        """Should validate score range."""
        opt = ResumeOptimization(
            match_score=85.5,
            ats_compatibility_score=90.0
        )
        assert opt.match_score == 85.5
    
    def test_score_out_of_range_raises_error(self):
        """Should raise error for scores outside 0-100."""
        with pytest.raises(ValueError):
            ResumeOptimization(
                match_score=150,
                ats_compatibility_score=90
            )


# ============================================================================
# AI Service Tests
# ============================================================================

class TestAIService:
    """Tests for AIService class."""
    
    @pytest.fixture
    def ai_service(self):
        """Create AI service instance for testing."""
        with patch('app.services.ai_service.settings') as mock_settings:
            mock_settings.OPENROUTER_API_KEY = "test-key"
            mock_settings.AI_MODEL = "test-model"
            mock_settings.OPENROUTER_MODEL = "test-model"
            service = AIService()
            return service
    
    def test_service_initialization(self, ai_service):
        """AI service should initialize with correct settings."""
        assert ai_service.api_url == "https://openrouter.ai/api/v1/chat/completions"
        assert ai_service.circuit_breaker is not None
    
    @pytest.mark.asyncio
    async def test_context_manager(self, ai_service):
        """AI service should work as async context manager."""
        async with ai_service as service:
            assert service.client is not None
        assert service.client is None or not hasattr(service.client, 'is_closed') or service.client.is_closed

    def test_extract_json_from_markdown_response(self, ai_service):
        """Should extract JSON from markdown code blocks."""
        content = '''Here is the analysis:
```json
{"job_title": "Engineer", "skills": ["Python"]}
```
That's the result.'''
        
        result = ai_service._extract_json_from_response(content)
        assert result["job_title"] == "Engineer"
        assert "Python" in result["skills"]
    
    def test_extract_json_from_direct_response(self, ai_service):
        """Should extract JSON from direct JSON response."""
        content = '{"job_title": "Engineer", "skills": ["Python"]}'
        
        result = ai_service._extract_json_from_response(content)
        assert result["job_title"] == "Engineer"
    
    def test_extract_json_invalid_raises_error(self, ai_service):
        """Should raise error for invalid JSON."""
        content = "This is not valid JSON at all"
        
        with pytest.raises(AIInvalidResponseError):
            ai_service._extract_json_from_response(content)


# ============================================================================
# Job Description Analysis Tests
# ============================================================================

class TestJobDescriptionAnalysis:
    """Tests for job description analysis functionality."""
    
    @pytest.fixture
    def ai_service(self):
        """Create AI service instance for testing."""
        with patch('app.services.ai_service.settings') as mock_settings:
            mock_settings.OPENROUTER_API_KEY = "test-key"
            mock_settings.AI_MODEL = "test-model"
            mock_settings.OPENROUTER_MODEL = "test-model"
            return AIService()
    
    @pytest.mark.asyncio
    async def test_empty_job_description_raises_error(self, ai_service):
        """Should raise error for empty job description."""
        with pytest.raises(JobDescriptionInvalidError) as exc_info:
            await ai_service.analyze_job_description("")
        assert "empty" in str(exc_info.value.message).lower()
    
    @pytest.mark.asyncio
    async def test_short_job_description_raises_error(self, ai_service):
        """Should raise error for too short job description."""
        short_desc = "Engineer needed"
        with pytest.raises(JobDescriptionInvalidError) as exc_info:
            await ai_service.analyze_job_description(short_desc)
        assert "too short" in str(exc_info.value.message).lower()
    
    @pytest.mark.asyncio
    async def test_long_job_description_raises_error(self, ai_service):
        """Should raise error for too long job description."""
        long_desc = "A" * (MAX_JOB_DESCRIPTION_LENGTH + 1)
        with pytest.raises(JobDescriptionInvalidError) as exc_info:
            await ai_service.analyze_job_description(long_desc)
        assert "too long" in str(exc_info.value.message).lower()
    
    @pytest.mark.asyncio
    async def test_successful_job_analysis(self, ai_service, sample_job_description):
        """Should successfully analyze valid job description."""
        mock_response = {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "job_title": "Senior Software Engineer",
                        "company": "TechCorp Inc.",
                        "requirements": [
                            {"category": "technical_skill", "skill": "Python", "importance": "required"}
                        ],
                        "skills": ["Python", "JavaScript", "React"],
                        "keywords": ["software", "engineer", "python", "javascript", "react"],
                        "experience_level": "senior",
                        "education_requirements": ["Bachelor's in Computer Science"],
                        "responsibilities": ["Design and implement features"]
                    })
                }
            }]
        }
        
        with patch.object(ai_service, '_make_api_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            async with ai_service:
                result = await ai_service.analyze_job_description(sample_job_description)
            
            assert result.job_title == "Senior Software Engineer"
            assert "Python" in result.skills
            assert len(result.keywords) >= 5


# ============================================================================
# Resume Optimization Tests
# ============================================================================

class TestResumeOptimizationService:
    """Tests for resume optimization functionality."""
    
    @pytest.fixture
    def ai_service(self):
        """Create AI service instance."""
        with patch('app.services.ai_service.settings') as mock_settings:
            mock_settings.OPENROUTER_API_KEY = "test-key"
            mock_settings.AI_MODEL = "test-model"
            mock_settings.OPENROUTER_MODEL = "test-model"
            return AIService()
    
    @pytest.mark.asyncio
    async def test_successful_optimization(self, ai_service, sample_resume_data):
        """Should successfully optimize resume content."""
        job_analysis = JobAnalysis(
            job_title="Software Engineer",
            skills={"Python", "JavaScript", "React"},
            keywords=["software", "engineer", "python"]
        )
        
        mock_response = {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "match_score": 85,
                        "missing_skills": ["Docker"],
                        "matching_skills": ["Python", "JavaScript"],
                        "keyword_suggestions": ["agile", "scrum"],
                        "content_improvements": [
                            {"section": "summary", "suggestion": "Add more keywords"}
                        ],
                        "formatting_suggestions": ["Use bullet points"],
                        "ats_compatibility_score": 90
                    })
                }
            }]
        }
        
        with patch.object(ai_service, '_make_api_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            async with ai_service:
                result = await ai_service.optimize_resume_content(
                    sample_resume_data,
                    job_analysis,
                    OptimizationLevel.STANDARD
                )
            
            assert result.match_score == 85
            assert "Docker" in result.missing_skills
            assert result.ats_compatibility_score == 90
    
    @pytest.mark.asyncio
    async def test_optimization_levels(self, ai_service, sample_resume_data):
        """Should use correct optimization level."""
        job_analysis = JobAnalysis(job_title="Engineer", skills=set())
        
        mock_response = {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "match_score": 80,
                        "missing_skills": [],
                        "matching_skills": [],
                        "keyword_suggestions": [],
                        "content_improvements": [],
                        "formatting_suggestions": [],
                        "ats_compatibility_score": 85
                    })
                }
            }]
        }
        
        for level in OptimizationLevel:
            with patch.object(ai_service, '_make_api_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = mock_response
                
                async with ai_service:
                    await ai_service.optimize_resume_content(
                        sample_resume_data,
                        job_analysis,
                        level
                    )
                
                # Verify the level was passed in the request
                call_args = mock_request.call_args
                messages = call_args[0][0]
                assert any(level.value in str(msg) for msg in messages)


# ============================================================================
# API Error Handling Tests
# ============================================================================

class TestAPIErrorHandling:
    """Tests for API error handling."""
    
    @pytest.fixture
    def ai_service(self):
        """Create AI service instance."""
        with patch('app.services.ai_service.settings') as mock_settings:
            mock_settings.OPENROUTER_API_KEY = "test-key"
            mock_settings.AI_MODEL = "test-model"
            mock_settings.OPENROUTER_MODEL = "test-model"
            return AIService()
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_blocks_when_open(self, ai_service):
        """Should block requests when circuit breaker is open."""
        ai_service.circuit_breaker.state = CircuitBreakerState.OPEN
        ai_service.circuit_breaker.last_failure_time = datetime.utcnow()
        ai_service.circuit_breaker.timeout_seconds = 3600  # 1 hour
        
        async with ai_service:
            with pytest.raises(AIServiceUnavailableError) as exc_info:
                await ai_service._make_api_request([{"role": "user", "content": "test"}])
            
            assert "temporarily unavailable" in str(exc_info.value.message).lower()
    
    @pytest.mark.asyncio
    async def test_rate_limit_handling(self, ai_service):
        """Should handle rate limit errors correctly."""
        import httpx
        
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.text = "Rate limit exceeded"
        
        async with ai_service:
            with patch.object(ai_service.client, 'post', new_callable=AsyncMock) as mock_post:
                mock_post.return_value = mock_response
                
                with pytest.raises(AIRateLimitError):
                    await ai_service._make_api_request([{"role": "user", "content": "test"}])
                
                # Circuit breaker should record failure
                assert ai_service.circuit_breaker.failure_count > 0
    
    @pytest.mark.asyncio
    async def test_missing_choices_in_response(self, ai_service, sample_job_description):
        """Should handle missing choices in API response."""
        mock_response = {"data": "invalid"}
        
        with patch.object(ai_service, '_make_api_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            async with ai_service:
                with pytest.raises(AIInvalidResponseError):
                    await ai_service.analyze_job_description(sample_job_description)


# ============================================================================
# Singleton Pattern Tests
# ============================================================================

class TestAIServiceSingleton:
    """Tests for AI service singleton pattern."""
    
    @pytest.mark.asyncio
    async def test_get_ai_service_returns_same_instance(self):
        """Should return the same instance on multiple calls."""
        with patch('app.services.ai_service.settings') as mock_settings:
            mock_settings.OPENROUTER_API_KEY = "test-key"
            mock_settings.AI_MODEL = "test-model"
            mock_settings.OPENROUTER_MODEL = "test-model"
            
            # Reset singleton
            import app.services.ai_service as ai_module
            ai_module._ai_service_instance = None
            
            service1 = await get_ai_service()
            service2 = await get_ai_service()
            
            assert service1 is service2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
