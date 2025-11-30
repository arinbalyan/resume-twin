"""
Integration tests for AI-powered resume optimization workflow.

Tests the complete AI optimization pipeline including:
- Job description analysis
- Resume content optimization
- Skills gap analysis
- ATS compatibility scoring
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json
from uuid import uuid4

from app.services.ai_service import AIService, OptimizationLevel, JobAnalysis, ResumeOptimization
from app.core.exceptions import JobDescriptionInvalidError, AIServiceUnavailableError


@pytest.fixture
def sample_job_description():
    """Sample job description for testing."""
    return """
    Senior Full-Stack Developer

    We are seeking an experienced full-stack developer to join our team.

    Requirements:
    - 5+ years of experience with Python and JavaScript
    - Strong proficiency in React and FastAPI
    - Experience with PostgreSQL and MongoDB
    - Knowledge of Docker and Kubernetes
    - Bachelor's degree in Computer Science or related field

    Preferred:
    - Experience with AWS or GCP
    - Knowledge of CI/CD pipelines
    - Previous experience in fintech

    Responsibilities:
    - Design and implement scalable web applications
    - Collaborate with cross-functional teams
    - Mentor junior developers
    - Contribute to architectural decisions
    """


@pytest.fixture
def sample_user_profile():
    """Sample user profile for testing."""
    return {
        "user_id": str(uuid4()),
        "full_name": "Jane Developer",
        "current_title": "Software Engineer",
        "bio": "Passionate full-stack developer with 4 years of experience",
        "experience_years": 4,
        "skills": [
            "Python", "JavaScript", "React", "FastAPI", 
            "PostgreSQL", "Docker", "Git"
        ],
        "projects": [
            {
                "title": "E-Commerce Platform",
                "description": "Built a scalable e-commerce platform using React and FastAPI",
                "technologies": ["React", "FastAPI", "PostgreSQL", "Docker"],
                "category": "Web Development"
            },
            {
                "title": "Task Management API",
                "description": "RESTful API for task management with authentication",
                "technologies": ["Python", "FastAPI", "MongoDB"],
                "category": "Backend Development"
            }
        ],
        "education": [
            {
                "institution": "State University",
                "degree": "Bachelor of Science",
                "field_of_study": "Computer Science",
                "graduation_year": 2020
            }
        ],
        "certifications": [
            {
                "name": "AWS Certified Developer",
                "issuer": "Amazon Web Services",
                "skills_acquired": ["AWS", "Lambda", "S3"]
            }
        ],
        "internships": [],
        "courses": [
            {
                "name": "Advanced React Patterns",
                "institution": "Frontend Masters",
                "skills_acquired": ["React", "TypeScript"]
            }
        ]
    }


class TestJobDescriptionAnalysis:
    """Test job description analysis functionality."""
    
    @pytest.mark.asyncio
    async def test_analyze_valid_job_description(
        self, 
        sample_job_description
    ):
        """Test analyzing a valid job description."""
        ai_service = AIService()
        
        # Mock the API response
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "job_title": "Senior Full-Stack Developer",
                            "company": None,
                            "requirements": [
                                {
                                    "category": "technical_skill",
                                    "skill": "Python",
                                    "importance": "required",
                                    "years_experience": 5
                                },
                                {
                                    "category": "technical_skill",
                                    "skill": "React",
                                    "importance": "required",
                                    "years_experience": None
                                }
                            ],
                            "skills": ["Python", "JavaScript", "React", "FastAPI", "PostgreSQL"],
                            "keywords": ["scalable", "full-stack", "microservices", "API", "database"],
                            "experience_level": "senior",
                            "education_requirements": ["Bachelor's in Computer Science"],
                            "responsibilities": ["Design applications", "Mentor developers"]
                        })
                    }
                }
            ]
        }
        
        with patch.object(ai_service, '_make_api_request', return_value=mock_response):
            async with ai_service:
                analysis = await ai_service.analyze_job_description(sample_job_description)
        
        assert isinstance(analysis, JobAnalysis)
        assert analysis.job_title == "Senior Full-Stack Developer"
        assert "Python" in analysis.skills
        assert len(analysis.keywords) >= 5
        assert analysis.experience_level == "senior"
    
    @pytest.mark.asyncio
    async def test_analyze_empty_job_description(self):
        """Test that empty job description raises error."""
        ai_service = AIService()
        
        with pytest.raises(JobDescriptionInvalidError):
            async with ai_service:
                await ai_service.analyze_job_description("")
    
    @pytest.mark.asyncio
    async def test_analyze_too_short_job_description(self):
        """Test that too short job description raises error."""
        ai_service = AIService()
        short_description = "We need a developer."
        
        with pytest.raises(JobDescriptionInvalidError):
            async with ai_service:
                await ai_service.analyze_job_description(short_description)


class TestResumeOptimization:
    """Test resume optimization functionality."""
    
    @pytest.mark.asyncio
    async def test_optimize_resume_standard_level(
        self,
        sample_user_profile,
        sample_job_description
    ):
        """Test resume optimization at standard level."""
        ai_service = AIService()
        
        # Mock job analysis
        job_analysis = JobAnalysis(
            job_title="Senior Full-Stack Developer",
            skills={"Python", "React", "FastAPI", "PostgreSQL", "Docker", "Kubernetes"},
            keywords=["scalable", "full-stack", "API", "microservices"],
            requirements=[],
            experience_level="senior",
            education_requirements=["Bachelor's in CS"]
        )
        
        # Mock optimization response
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "match_score": 78.5,
                            "missing_skills": ["Kubernetes", "CI/CD"],
                            "matching_skills": ["Python", "React", "FastAPI", "PostgreSQL", "Docker"],
                            "keyword_suggestions": ["microservices", "scalable architecture", "RESTful"],
                            "content_improvements": [
                                {
                                    "section": "experience",
                                    "suggestion": "Add metrics to quantify impact"
                                },
                                {
                                    "section": "projects",
                                    "suggestion": "Highlight scalability aspects"
                                }
                            ],
                            "formatting_suggestions": [
                                "Use action verbs at start of bullet points",
                                "Add quantifiable achievements"
                            ],
                            "ats_compatibility_score": 85.0
                        })
                    }
                }
            ]
        }
        
        with patch.object(ai_service, '_make_api_request', return_value=mock_response):
            async with ai_service:
                optimization = await ai_service.optimize_resume_content(
                    user_profile=sample_user_profile,
                    job_analysis=job_analysis,
                    optimization_level=OptimizationLevel.STANDARD
                )
        
        assert isinstance(optimization, ResumeOptimization)
        assert 0 <= optimization.match_score <= 100
        assert 0 <= optimization.ats_compatibility_score <= 100
        assert len(optimization.missing_skills) > 0
        assert len(optimization.matching_skills) > 0
        assert "Kubernetes" in optimization.missing_skills
    
    @pytest.mark.asyncio
    async def test_optimize_resume_advanced_level(
        self,
        sample_user_profile
    ):
        """Test resume optimization at advanced level."""
        ai_service = AIService()
        
        job_analysis = JobAnalysis(
            job_title="Lead Software Engineer",
            skills={"Python", "React", "AWS", "Leadership"},
            keywords=["architecture", "leadership", "mentoring"],
            requirements=[]
        )
        
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "match_score": 82.0,
                            "missing_skills": ["AWS", "Leadership experience"],
                            "matching_skills": ["Python", "React"],
                            "keyword_suggestions": ["technical leadership", "architecture design"],
                            "content_improvements": [
                                {
                                    "section": "summary",
                                    "suggestion": "Emphasize leadership experience"
                                }
                            ],
                            "formatting_suggestions": ["Add leadership section"],
                            "ats_compatibility_score": 88.0
                        })
                    }
                }
            ]
        }
        
        with patch.object(ai_service, '_make_api_request', return_value=mock_response):
            async with ai_service:
                optimization = await ai_service.optimize_resume_content(
                    user_profile=sample_user_profile,
                    job_analysis=job_analysis,
                    optimization_level=OptimizationLevel.ADVANCED
                )
        
        assert optimization.match_score > 80
        assert optimization.ats_compatibility_score > 85


class TestSkillsGapAnalysis:
    """Test skills gap analysis."""
    
    def test_identify_missing_skills(self, sample_user_profile):
        """Test identification of missing skills."""
        user_skills = set(sample_user_profile["skills"])
        job_skills = {"Python", "React", "FastAPI", "Kubernetes", "AWS", "TypeScript"}
        
        missing_skills = job_skills - user_skills
        matching_skills = job_skills & user_skills
        
        assert "Kubernetes" in missing_skills
        assert "AWS" in missing_skills
        assert "Python" in matching_skills
        assert "React" in matching_skills
        assert len(matching_skills) >= 3
    
    def test_skill_match_percentage(self, sample_user_profile):
        """Test calculation of skill match percentage."""
        user_skills = set(sample_user_profile["skills"])
        job_skills = {"Python", "React", "FastAPI", "PostgreSQL", "Docker", "Kubernetes"}
        
        matching = len(job_skills & user_skills)
        total = len(job_skills)
        match_percentage = (matching / total) * 100
        
        assert match_percentage > 0
        assert match_percentage <= 100
        # User has 5 out of 6 skills = 83.3%
        assert match_percentage > 80


class TestATSCompatibility:
    """Test ATS (Applicant Tracking System) compatibility scoring."""
    
    def test_keyword_density_analysis(self):
        """Test keyword density in resume content."""
        resume_text = """
        Senior Full-Stack Developer with 5 years of experience in Python and React.
        Built scalable microservices using FastAPI and PostgreSQL.
        Experienced in Docker containerization and cloud deployments.
        """
        
        target_keywords = ["Python", "React", "FastAPI", "scalable", "microservices"]
        
        keyword_count = sum(1 for keyword in target_keywords if keyword in resume_text)
        keyword_density = (keyword_count / len(target_keywords)) * 100
        
        assert keyword_density > 80  # Good keyword coverage
    
    def test_section_presence_check(self):
        """Test presence of key resume sections."""
        resume_sections = {
            "summary": True,
            "experience": True,
            "education": True,
            "skills": True,
            "projects": True,
            "certifications": False  # Optional
        }
        
        required_sections = ["summary", "experience", "education", "skills"]
        has_required = all(resume_sections.get(section, False) for section in required_sections)
        
        assert has_required is True


class TestContentOptimization:
    """Test content optimization suggestions."""
    
    def test_quantify_achievements(self):
        """Test suggestions for quantifying achievements."""
        original = "Improved system performance"
        optimized = "Improved system performance by 40%, reducing response time from 2s to 1.2s"
        
        # Check that optimized version has numbers
        has_metrics = any(char.isdigit() for char in optimized)
        assert has_metrics is True
        assert len(optimized) > len(original)
    
    def test_action_verb_usage(self):
        """Test use of strong action verbs."""
        weak_verbs = ["did", "worked on", "helped with"]
        strong_verbs = ["architected", "implemented", "optimized", "led", "designed"]
        
        # Strong verbs are more impactful
        assert len(strong_verbs) > 0
        assert all(verb not in weak_verbs for verb in strong_verbs)


@pytest.mark.integration
class TestEndToEndOptimization:
    """End-to-end integration tests for AI optimization."""
    
    @pytest.mark.asyncio
    async def test_complete_optimization_workflow(
        self,
        sample_job_description,
        sample_user_profile
    ):
        """Test the complete optimization workflow."""
        ai_service = AIService()
        
        # Mock responses for both API calls
        job_analysis_response = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "job_title": "Senior Full-Stack Developer",
                            "company": "Tech Corp",
                            "requirements": [],
                            "skills": ["Python", "React", "FastAPI"],
                            "keywords": ["scalable", "microservices"],
                            "experience_level": "senior",
                            "education_requirements": ["Bachelor's"],
                            "responsibilities": ["Design", "Develop"]
                        })
                    }
                }
            ]
        }
        
        optimization_response = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "match_score": 85.0,
                            "missing_skills": ["Kubernetes"],
                            "matching_skills": ["Python", "React", "FastAPI"],
                            "keyword_suggestions": ["cloud-native", "DevOps"],
                            "content_improvements": [
                                {"section": "summary", "suggestion": "Add impact metrics"}
                            ],
                            "formatting_suggestions": ["Use bullet points"],
                            "ats_compatibility_score": 90.0
                        })
                    }
                }
            ]
        }
        
        with patch.object(
            ai_service, 
            '_make_api_request',
            side_effect=[job_analysis_response, optimization_response]
        ):
            async with ai_service:
                # Step 1: Analyze job
                job_analysis = await ai_service.analyze_job_description(sample_job_description)
                
                # Step 2: Optimize resume
                optimization = await ai_service.optimize_resume_content(
                    user_profile=sample_user_profile,
                    job_analysis=job_analysis,
                    optimization_level=OptimizationLevel.STANDARD
                )
        
        # Verify complete workflow
        assert job_analysis.job_title == "Senior Full-Stack Developer"
        assert optimization.match_score == 85.0
        assert optimization.ats_compatibility_score == 90.0
        assert len(optimization.content_improvements) > 0
    
    @pytest.mark.asyncio
    async def test_optimization_with_incomplete_profile(self):
        """Test optimization with incomplete user profile."""
        incomplete_profile = {
            "user_id": str(uuid4()),
            "full_name": "John Doe",
            "skills": ["Python"],
            "projects": [],
            "education": [],
            "certifications": [],
            "internships": [],
            "courses": []
        }
        
        job_analysis = JobAnalysis(
            job_title="Software Engineer",
            skills={"Python", "JavaScript", "React"},
            keywords=["backend", "API"],
            requirements=[]
        )
        
        ai_service = AIService()
        
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "match_score": 35.0,  # Low score due to incomplete profile
                            "missing_skills": ["JavaScript", "React"],
                            "matching_skills": ["Python"],
                            "keyword_suggestions": ["Add more skills"],
                            "content_improvements": [
                                {"section": "overall", "suggestion": "Complete your profile"}
                            ],
                            "formatting_suggestions": ["Add projects and education"],
                            "ats_compatibility_score": 45.0
                        })
                    }
                }
            ]
        }
        
        with patch.object(ai_service, '_make_api_request', return_value=mock_response):
            async with ai_service:
                optimization = await ai_service.optimize_resume_content(
                    user_profile=incomplete_profile,
                    job_analysis=job_analysis,
                    optimization_level=OptimizationLevel.BASIC
                )
        
        # Incomplete profile should result in lower scores
        assert optimization.match_score < 50
        assert optimization.ats_compatibility_score < 60
        assert len(optimization.missing_skills) > 0


class TestErrorHandling:
    """Test error handling in AI optimization."""
    
    @pytest.mark.asyncio
    async def test_handle_ai_service_unavailable(self):
        """Test handling when AI service is unavailable."""
        ai_service = AIService()
        ai_service.circuit_breaker.state = ai_service.circuit_breaker.state.OPEN
        
        with pytest.raises(AIServiceUnavailableError):
            async with ai_service:
                await ai_service._make_api_request([{"role": "user", "content": "test"}])
    
    @pytest.mark.asyncio
    async def test_handle_invalid_response(self):
        """Test handling of invalid AI responses."""
        ai_service = AIService()
        
        # Mock invalid response
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "This is not valid JSON"
                    }
                }
            ]
        }
        
        with patch.object(ai_service, '_make_api_request', return_value=mock_response):
            async with ai_service:
                with pytest.raises(Exception):  # Should raise parsing error
                    await ai_service.analyze_job_description("Test job description" * 10)
