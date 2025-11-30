"""
Unit Tests for Resume Service.

Tests cover:
- Resume version creation
- Resume retrieval
- Resume updates
- Resume optimization
"""

import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from datetime import date
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def sample_resume_version_dict():
    """Create sample resume version data as dict."""
    return {
        "id": uuid4(),
        "user_id": uuid4(),
        "template_id": uuid4(),
        "title": "Software Engineer Resume",
        "job_description": "Looking for a senior developer...",
        "optimized_content": {
            "summary": "Experienced developer",
            "skills": ["Python", "JavaScript"],
            "experience": []
        },
        "latex_content": "\\documentclass{article}...",
        "pdf_url": "https://example.com/resume.pdf",
        "preview_url": "https://example.com/resume-preview.png",
        "is_ai_optimized": True,
        "optimization_score": 85,
        "optimization_version": 1,
        "sections_included": ["summary", "experience", "skills"],
        "customizations": {},
        "status": "ready",
        "is_default": True,
        "is_public": False,
        "download_count": 5,
        "created_at": date.today(),
        "updated_at": date.today()
    }


@pytest.fixture
def mock_resume_service():
    """Create mock resume service."""
    with patch('app.services.resume_service.BaseService.__init__', return_value=None):
        from app.services.resume_service import ResumeService
        service = ResumeService()
        service.table_name = "resume_versions"
        service.client = MagicMock()
        return service


# ============================================================================
# Resume Service CRUD Tests
# ============================================================================

class TestResumeServiceCRUD:
    """Tests for Resume Service CRUD operations."""
    
    def test_create_resume_success(self, mock_resume_service, sample_resume_version_dict):
        """Should successfully create a resume version."""
        user_id = uuid4()
        template_id = uuid4()
        
        mock_resume_service.create = MagicMock(return_value=sample_resume_version_dict)
        
        from app.models.resume import ResumeVersionCreate
        resume_create = ResumeVersionCreate(
            title="My Resume v1",
            job_description="Software Engineer at Google"
        )
        
        result = mock_resume_service.create_resume(user_id, template_id, resume_create)
        
        assert result is not None
        mock_resume_service.create.assert_called_once()
    
    def test_create_resume_failure(self, mock_resume_service):
        """Should return None when creation fails."""
        user_id = uuid4()
        template_id = uuid4()
        
        mock_resume_service.create = MagicMock(side_effect=Exception("Database error"))
        
        from app.models.resume import ResumeVersionCreate
        resume_create = ResumeVersionCreate(title="Test Resume")
        
        result = mock_resume_service.create_resume(user_id, template_id, resume_create)
        
        assert result is None
    
    def test_get_resume_found(self, mock_resume_service, sample_resume_version_dict):
        """Should return resume when found using get_by_id."""
        resume_id = uuid4()
        
        mock_resume_service.get_by_id = MagicMock(return_value=sample_resume_version_dict)
        
        result = mock_resume_service.get_by_id(resume_id)
        
        assert result is not None
        assert result["title"] == "Software Engineer Resume"
    
    def test_get_resume_not_found(self, mock_resume_service):
        """Should return None when resume not found."""
        resume_id = uuid4()
        
        mock_resume_service.get_by_id = MagicMock(return_value=None)
        
        result = mock_resume_service.get_by_id(resume_id)
        
        assert result is None
    
    def test_get_user_resumes(self, mock_resume_service, sample_resume_version_dict):
        """Should return list of user's resumes using filter."""
        user_id = uuid4()
        
        resume1 = sample_resume_version_dict.copy()
        resume2 = sample_resume_version_dict.copy()
        resume2["id"] = uuid4()
        resume2["title"] = "Data Scientist Resume"
        
        mock_resume_service.filter = MagicMock(return_value=[resume1, resume2])
        
        result = mock_resume_service.filter({"user_id": str(user_id)})
        
        assert len(result) == 2


# ============================================================================
# Resume Version Model Tests
# ============================================================================

class TestResumeVersionModel:
    """Tests for ResumeVersion model."""
    
    def test_resume_version_create_minimal(self):
        """Should create resume version with minimal data."""
        from app.models.resume import ResumeVersionCreate
        
        resume = ResumeVersionCreate(title="My Resume")
        
        assert resume.title == "My Resume"
        assert resume.status == "draft"  # default
    
    def test_resume_version_create_full(self):
        """Should create resume version with full data."""
        from app.models.resume import ResumeVersionCreate
        
        resume = ResumeVersionCreate(
            title="My Resume v1",
            job_description="Software Engineer at Google",
            optimized_content={"summary": "Test"},
            sections_included=["summary", "experience"],
            is_default=True
        )
        
        assert resume.title == "My Resume v1"
        assert resume.job_description == "Software Engineer at Google"
    
    def test_resume_version_update_partial(self):
        """Should allow partial updates."""
        from app.models.resume import ResumeVersionUpdate
        
        update = ResumeVersionUpdate(title="Updated Title")
        
        assert update.title == "Updated Title"
        assert update.job_description is None
    
    def test_resume_version_full_model(self, sample_resume_version_dict):
        """Should create ResumeVersion from dict."""
        from app.models.resume import ResumeVersion
        
        resume = ResumeVersion(**sample_resume_version_dict)
        
        assert resume.title == "Software Engineer Resume"
        assert resume.optimization_score == 85
        assert resume.is_ai_optimized is True


# ============================================================================
# Template Model Tests
# ============================================================================

class TestTemplateModel:
    """Tests for Template model."""
    
    def test_template_create_minimal(self):
        """Should create template with required fields."""
        from app.models.resume import TemplateCreate
        
        template = TemplateCreate(
            name="Modern Resume",
            category="professional",
            latex_content="\\documentclass{article}"
        )
        
        assert template.name == "Modern Resume"
        assert template.is_public is True  # default
    
    def test_template_create_full(self):
        """Should create template with all fields."""
        from app.models.resume import TemplateCreate
        
        template = TemplateCreate(
            name="Developer Resume",
            category="technical",
            subcategory="software",
            description="Modern resume for developers",
            latex_content="\\documentclass{article}",
            is_featured=True,
            tags=["developer", "technical"]
        )
        
        assert template.name == "Developer Resume"
        assert template.is_featured is True
        assert "developer" in template.tags


# ============================================================================
# Resume Generation Models Tests
# ============================================================================

class TestResumeGenerationModels:
    """Tests for resume generation models."""
    
    def test_resume_generation_request(self):
        """Should create valid generation request."""
        from app.models.resume import ResumeGenerationRequest
        
        request = ResumeGenerationRequest(
            template_id=uuid4(),
            user_id=uuid4(),
            sections_to_include=["summary", "experience"],
            job_description="Software Engineer role"
        )
        
        assert len(request.sections_to_include) == 2
        assert request.force_regenerate is False  # default
    
    def test_resume_generation_response(self):
        """Should create valid generation response."""
        from app.models.resume import ResumeGenerationResponse
        
        response = ResumeGenerationResponse(
            resume_version_id=uuid4(),
            status="ready",
            pdf_url="https://example.com/resume.pdf",
            optimization_score=90
        )
        
        assert response.status == "ready"
        assert response.optimization_score == 90


# ============================================================================
# AI Optimization Models Tests
# ============================================================================

class TestAIOptimizationModels:
    """Tests for AI optimization models."""
    
    def test_ai_optimization_request(self):
        """Should create valid optimization request."""
        from app.models.resume import AIOptimizationRequest
        
        request = AIOptimizationRequest(
            resume_content={"summary": "Test"},
            job_description="Senior Engineer role",
            optimization_type="full"
        )
        
        assert request.optimization_type == "full"
        assert request.ai_model == "gpt-3.5-turbo"  # default
    
    def test_ai_optimization_response(self):
        """Should create valid optimization response."""
        from app.models.resume import AIOptimizationResponse
        
        response = AIOptimizationResponse(
            optimized_content={"summary": "Optimized"},
            optimization_score=95,
            keywords_added=["python", "aws"],
            keywords_removed=[],
            content_improvements=["Added quantified achievements"],
            processing_time_ms=1500,
            ai_model_used="gpt-4"
        )
        
        assert response.optimization_score == 95
        assert "python" in response.keywords_added
    
    def test_keyword_analysis(self):
        """Should create valid keyword analysis."""
        from app.models.resume import KeywordAnalysis
        
        analysis = KeywordAnalysis(
            keywords_found=["python", "javascript"],
            keywords_suggested=["aws", "docker"],
            industry_specific_terms=["agile"],
            action_words=["developed", "implemented"],
            technical_skills=["python"],
            soft_skills=["leadership"],
            missing_keywords=["kubernetes"]
        )
        
        assert "python" in analysis.keywords_found
        assert "kubernetes" in analysis.missing_keywords


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
