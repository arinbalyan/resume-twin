"""
Unit Tests for Resume Scorer Service.

Tests cover:
- Overall resume scoring
- Section-by-section scoring (contact, summary, experience, skills, projects, education)
- ATS compatibility scoring
- Job description keyword matching
- Improvement suggestions generation
- Score validation
"""

import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.resume_scorer_service import ResumeScorer, ScoringResult


# ============================================================================
# Resume Scorer Initialization Tests
# ============================================================================

class TestResumeScorerInit:
    """Tests for Resume Scorer initialization."""
    
    def test_scorer_initialization(self):
        """Should initialize with action verbs and tech skills."""
        scorer = ResumeScorer()
        
        assert len(scorer.ACTION_VERBS) > 0
        assert "developed" in scorer.ACTION_VERBS
        assert "led" in scorer.ACTION_VERBS
        
        assert "languages" in scorer.TECH_SKILLS
        assert "python" in scorer.TECH_SKILLS["languages"]


# ============================================================================
# Contact Section Scoring Tests
# ============================================================================

class TestContactScoring:
    """Tests for contact section scoring."""
    
    @pytest.fixture
    def scorer(self):
        """Create scorer instance."""
        return ResumeScorer()
    
    def test_complete_contact_info(self, scorer):
        """Should score high for complete contact info."""
        resume_data = {
            "user_name": "John Doe",
            "email": "john@example.com",
            "phone": "+1-555-123-4567",
            "linkedin": "https://linkedin.com/in/johndoe",
            "github": "https://github.com/johndoe",
            "location": "San Francisco, CA"
        }
        
        issues = []
        suggestions = []
        score = scorer._score_contact(resume_data, issues, suggestions)
        
        assert score >= 90
        assert len(issues) == 0
    
    def test_missing_name(self, scorer):
        """Should flag missing name as error."""
        resume_data = {
            "email": "john@example.com"
        }
        
        issues = []
        suggestions = []
        score = scorer._score_contact(resume_data, issues, suggestions)
        
        assert score < 50
        assert any(i["severity"] == "error" and "name" in i["message"].lower() for i in issues)
    
    def test_missing_email(self, scorer):
        """Should flag missing email as error."""
        resume_data = {
            "user_name": "John Doe"
        }
        
        issues = []
        suggestions = []
        score = scorer._score_contact(resume_data, issues, suggestions)
        
        assert any(i["severity"] == "error" and "email" in i["message"].lower() for i in issues)
    
    def test_invalid_email_format(self, scorer):
        """Should flag invalid email format."""
        resume_data = {
            "user_name": "John Doe",
            "email": "invalid-email"
        }
        
        issues = []
        suggestions = []
        score = scorer._score_contact(resume_data, issues, suggestions)
        
        assert any(i["severity"] == "warning" and "email" in i["message"].lower() for i in issues)
    
    def test_missing_linkedin_suggestion(self, scorer):
        """Should suggest adding LinkedIn."""
        resume_data = {
            "user_name": "John Doe",
            "email": "john@example.com"
        }
        
        issues = []
        suggestions = []
        scorer._score_contact(resume_data, issues, suggestions)
        
        assert any("linkedin" in s.lower() for s in suggestions)


# ============================================================================
# Summary Section Scoring Tests
# ============================================================================

class TestSummaryScoring:
    """Tests for summary section scoring."""
    
    @pytest.fixture
    def scorer(self):
        """Create scorer instance."""
        return ResumeScorer()
    
    def test_no_summary(self, scorer):
        """Should score 0 for missing summary."""
        resume_data = {}
        
        issues = []
        suggestions = []
        score = scorer._score_summary(resume_data, issues, suggestions)
        
        assert score == 0
        assert any(i["section"] == "summary" for i in issues)
    
    def test_short_summary(self, scorer):
        """Should flag too short summary."""
        resume_data = {
            "summary": "I am a developer."
        }
        
        issues = []
        suggestions = []
        score = scorer._score_summary(resume_data, issues, suggestions)
        
        assert score > 0  # Has a summary
        assert any("too short" in i["message"].lower() for i in issues)
    
    def test_good_summary_with_action_verbs(self, scorer):
        """Should score higher for summary with action verbs."""
        resume_data = {
            "summary": """Experienced software engineer who has developed and led multiple 
            high-impact projects. Achieved 40% improvement in system performance. 
            Managed teams of 5+ engineers and delivered products on time."""
        }
        
        issues = []
        suggestions = []
        score = scorer._score_summary(resume_data, issues, suggestions)
        
        assert score >= 70
    
    def test_summary_with_quantifiable_achievements(self, scorer):
        """Should score higher for quantifiable achievements."""
        resume_data = {
            "summary": """Software engineer with 10+ years of experience. 
            Improved system performance by 50%. Managed $2M budget projects.
            Led a team delivering 100% on-time releases."""
        }
        
        issues = []
        suggestions = []
        score = scorer._score_summary(resume_data, issues, suggestions)
        
        assert score >= 80


# ============================================================================
# Experience Section Scoring Tests
# ============================================================================

class TestExperienceScoring:
    """Tests for experience section scoring."""
    
    @pytest.fixture
    def scorer(self):
        """Create scorer instance."""
        return ResumeScorer()
    
    def test_no_experience(self, scorer):
        """Should score 0 for missing experience."""
        resume_data = {}
        
        issues = []
        suggestions = []
        score = scorer._score_experience(resume_data, issues, suggestions)
        
        assert score == 0
        assert any(i["section"] == "experience" for i in issues)
    
    def test_experience_with_few_bullets(self, scorer):
        """Should suggest more bullet points."""
        resume_data = {
            "experience": [
                {
                    "position": "Developer",
                    "company": "TechCorp",
                    "achievements": ["Did some work"]
                }
            ]
        }
        
        issues = []
        suggestions = []
        score = scorer._score_experience(resume_data, issues, suggestions)
        
        assert any("bullet points" in s.lower() for s in suggestions)
    
    def test_experience_with_action_verbs(self, scorer):
        """Should score higher for action verb usage."""
        resume_data = {
            "experience": [
                {
                    "position": "Senior Developer",
                    "company": "TechCorp",
                    "achievements": [
                        "Developed microservices architecture serving 1M users",
                        "Led team of 5 engineers",
                        "Implemented CI/CD pipeline reducing deployment time",
                        "Achieved 99.9% uptime"
                    ]
                }
            ]
        }
        
        issues = []
        suggestions = []
        score = scorer._score_experience(resume_data, issues, suggestions)
        
        assert score >= 60
    
    def test_experience_with_metrics(self, scorer):
        """Should score higher for quantified achievements."""
        resume_data = {
            "experience": [
                {
                    "position": "Software Engineer",
                    "company": "StartupXYZ",
                    "achievements": [
                        "Reduced API response time by 60%",
                        "Saved $50,000 annually through automation",
                        "Increased user engagement by 40%",
                        "Managed team of 3 developers"
                    ]
                },
                {
                    "position": "Junior Developer",
                    "company": "Tech Inc",
                    "achievements": [
                        "Improved test coverage to 90%",
                        "Fixed 100+ bugs in first quarter",
                        "Reduced load time by 2 seconds"
                    ]
                }
            ]
        }
        
        issues = []
        suggestions = []
        score = scorer._score_experience(resume_data, issues, suggestions)
        
        assert score >= 70


# ============================================================================
# Skills Section Scoring Tests
# ============================================================================

class TestSkillsScoring:
    """Tests for skills section scoring."""
    
    @pytest.fixture
    def scorer(self):
        """Create scorer instance."""
        return ResumeScorer()
    
    def test_no_skills(self, scorer):
        """Should score 0 for missing skills."""
        resume_data = {}
        
        issues = []
        suggestions = []
        score = scorer._score_skills(resume_data, issues, suggestions)
        
        assert score == 0
    
    def test_few_skills(self, scorer):
        """Should suggest adding more skills."""
        resume_data = {
            "skills": ["Python", "JavaScript"]
        }
        
        issues = []
        suggestions = []
        score = scorer._score_skills(resume_data, issues, suggestions)
        
        assert any("more skills" in s.lower() for s in suggestions)
    
    def test_skills_as_dictionary(self, scorer):
        """Should handle skills organized by category."""
        resume_data = {
            "skills": {
                "Languages": ["Python", "JavaScript", "TypeScript", "Go"],
                "Frameworks": ["React", "FastAPI", "Django"],
                "Databases": ["PostgreSQL", "MongoDB", "Redis"],
                "Cloud": ["AWS", "Docker", "Kubernetes"]
            }
        }
        
        issues = []
        suggestions = []
        score = scorer._score_skills(resume_data, issues, suggestions)
        
        assert score >= 80
    
    def test_skills_as_list(self, scorer):
        """Should handle skills as a flat list."""
        resume_data = {
            "skills": [
                "Python", "JavaScript", "React", "Node.js", 
                "PostgreSQL", "Docker", "AWS", "Git",
                "REST APIs", "GraphQL"
            ]
        }
        
        issues = []
        suggestions = []
        score = scorer._score_skills(resume_data, issues, suggestions)
        
        assert score >= 60


# ============================================================================
# Projects Section Scoring Tests
# ============================================================================

class TestProjectsScoring:
    """Tests for projects section scoring."""
    
    @pytest.fixture
    def scorer(self):
        """Create scorer instance."""
        return ResumeScorer()
    
    def test_no_projects(self, scorer):
        """Should give base score for missing projects."""
        resume_data = {}
        
        issues = []
        suggestions = []
        score = scorer._score_projects(resume_data, issues, suggestions)
        
        # Should still get some score (30) even without projects
        assert score == 30
        assert any("project" in s.lower() for s in suggestions)
    
    def test_complete_projects(self, scorer):
        """Should score high for complete project information."""
        resume_data = {
            "projects": [
                {
                    "title": "Resume Twin",
                    "description": "AI-powered resume builder",
                    "technologies": ["Python", "FastAPI", "React"],
                    "github_url": "https://github.com/user/project",
                    "live_url": "https://project.com",
                    "bullet_points": ["Feature 1", "Feature 2"]
                },
                {
                    "title": "Analytics Dashboard",
                    "description": "Real-time analytics platform",
                    "technologies": ["TypeScript", "Next.js"],
                    "github_url": "https://github.com/user/analytics"
                }
            ]
        }
        
        issues = []
        suggestions = []
        score = scorer._score_projects(resume_data, issues, suggestions)
        
        assert score >= 70
    
    def test_projects_missing_descriptions(self, scorer):
        """Should suggest adding descriptions."""
        resume_data = {
            "projects": [
                {"title": "Project 1"},
                {"title": "Project 2", "description": "Has description"}
            ]
        }
        
        issues = []
        suggestions = []
        score = scorer._score_projects(resume_data, issues, suggestions)
        
        assert any("description" in s.lower() for s in suggestions)


# ============================================================================
# Education Section Scoring Tests
# ============================================================================

class TestEducationScoring:
    """Tests for education section scoring."""
    
    @pytest.fixture
    def scorer(self):
        """Create scorer instance."""
        return ResumeScorer()
    
    def test_no_education(self, scorer):
        """Should note missing education."""
        resume_data = {}
        
        issues = []
        suggestions = []
        score = scorer._score_education(resume_data, issues, suggestions)
        
        assert score == 0
        assert any(i["section"] == "education" for i in issues)
    
    def test_education_with_degree(self, scorer):
        """Should score for degree and institution."""
        resume_data = {
            "education": [
                {
                    "degree": "Bachelor of Science in Computer Science",
                    "institution": "Stanford University",
                    "year": "2020",
                    "gpa": "3.8"
                }
            ]
        }
        
        issues = []
        suggestions = []
        score = scorer._score_education(resume_data, issues, suggestions)
        
        assert score >= 75
    
    def test_education_with_certifications(self, scorer):
        """Should give bonus for certifications."""
        resume_data = {
            "education": [
                {"degree": "BS Computer Science", "institution": "MIT"}
            ],
            "certifications": [
                "AWS Solutions Architect",
                "Google Cloud Professional"
            ]
        }
        
        issues = []
        suggestions = []
        score = scorer._score_education(resume_data, issues, suggestions)
        
        assert score >= 80


# ============================================================================
# ATS Compatibility Scoring Tests
# ============================================================================

class TestATSCompatibility:
    """Tests for ATS compatibility scoring."""
    
    @pytest.fixture
    def scorer(self):
        """Create scorer instance."""
        return ResumeScorer()
    
    def test_ats_standard_sections(self, scorer):
        """Should score higher for standard section names."""
        resume_data = {
            "summary": "Professional summary here",
            "experience": [{"position": "Developer"}],
            "education": [{"degree": "BS"}],
            "skills": ["Python"]
        }
        
        issues = []
        suggestions = []
        score = scorer._score_ats_compatibility(resume_data, issues, suggestions)
        
        assert score >= 80
    
    def test_ats_special_characters_in_name(self, scorer):
        """Should flag special characters in name."""
        resume_data = {
            "user_name": "John Doe™ (The Best!)",
            "summary": "Summary",
            "experience": [],
            "education": [],
            "skills": []
        }
        
        issues = []
        suggestions = []
        score = scorer._score_ats_compatibility(resume_data, issues, suggestions)
        
        assert any(i["section"] == "ats" for i in issues)


# ============================================================================
# Job Description Matching Tests
# ============================================================================

class TestJobDescriptionMatching:
    """Tests for job description keyword matching."""
    
    @pytest.fixture
    def scorer(self):
        """Create scorer instance."""
        return ResumeScorer()
    
    def test_keyword_matching(self, scorer):
        """Should find keyword matches."""
        resume_data = {
            "summary": "Python developer with React experience",
            "skills": ["Python", "JavaScript", "React", "AWS"],
            "experience": [
                {"position": "Developer", "achievements": ["Built APIs"]}
            ]
        }
        
        job_description = """
        Looking for a Python developer with experience in React.
        Must have AWS and JavaScript skills.
        """
        
        matches = scorer._match_job_keywords(resume_data, job_description)
        
        assert "python" in matches
        assert "react" in matches
    
    def test_match_score_calculation(self, scorer):
        """Should calculate match score based on keywords."""
        keyword_matches = {
            "python": 5,
            "react": 3,
            "javascript": 2,
            "aws": 1,
            "docker": 1
        }
        
        score = scorer._calculate_jd_match_score(keyword_matches)
        
        assert score >= 50


# ============================================================================
# Overall Scoring Tests
# ============================================================================

class TestOverallScoring:
    """Tests for overall resume scoring."""
    
    @pytest.fixture
    def scorer(self):
        """Create scorer instance."""
        return ResumeScorer()
    
    def test_score_resume_returns_scoring_result(self, scorer, sample_resume_data):
        """Should return ScoringResult object."""
        result = scorer.score_resume(sample_resume_data)
        
        assert isinstance(result, ScoringResult)
        assert 0 <= result.overall_score <= 100
        assert "contact" in result.category_scores
        assert "experience" in result.category_scores
    
    def test_score_resume_with_job_description(self, scorer, sample_resume_data, sample_job_description):
        """Should include keyword matches when job description provided."""
        result = scorer.score_resume(sample_resume_data, sample_job_description)
        
        assert len(result.keyword_matches) > 0
    
    def test_high_quality_resume_scores_high(self, scorer):
        """Should score high for well-crafted resume."""
        high_quality_resume = {
            "user_name": "John Doe",
            "email": "john@example.com",
            "phone": "+1-555-123-4567",
            "linkedin": "https://linkedin.com/in/johndoe",
            "github": "https://github.com/johndoe",
            "location": "San Francisco, CA",
            "summary": """Senior Software Engineer with 10+ years of experience 
            developing scalable applications. Led teams of 5+ engineers, achieving 
            40% improvement in system performance. Expert in Python, JavaScript, 
            and cloud technologies.""",
            "skills": {
                "Languages": ["Python", "JavaScript", "TypeScript", "Go"],
                "Frameworks": ["React", "FastAPI", "Django", "Node.js"],
                "Databases": ["PostgreSQL", "MongoDB", "Redis"],
                "Cloud": ["AWS", "Docker", "Kubernetes", "Terraform"]
            },
            "experience": [
                {
                    "position": "Senior Software Engineer",
                    "company": "TechCorp",
                    "achievements": [
                        "Developed microservices architecture serving 1M+ users",
                        "Reduced API response time by 60% through optimization",
                        "Mentored team of 5 junior developers",
                        "Implemented CI/CD pipeline reducing deployment time by 70%"
                    ]
                }
            ],
            "projects": [
                {
                    "title": "Open Source Analytics",
                    "description": "Real-time analytics dashboard",
                    "technologies": ["React", "Python", "PostgreSQL"],
                    "github_url": "https://github.com/johndoe/analytics",
                    "bullet_points": ["500+ GitHub stars", "Used by 50+ companies"]
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science in Computer Science",
                    "institution": "Stanford University",
                    "gpa": "3.8"
                }
            ],
            "certifications": ["AWS Solutions Architect", "Google Cloud Professional"]
        }
        
        result = scorer.score_resume(high_quality_resume)
        
        assert result.overall_score >= 75


# ============================================================================
# Improvement Priority Tests
# ============================================================================

class TestImprovementPriority:
    """Tests for improvement priority generation."""
    
    @pytest.fixture
    def scorer(self):
        """Create scorer instance."""
        return ResumeScorer()
    
    def test_get_improvement_priority(self, scorer):
        """Should return prioritized improvements."""
        result = ScoringResult(
            overall_score=60,
            category_scores={
                "contact": 90,
                "summary": 45,
                "experience": 65,
                "skills": 80,
                "projects": 30,
                "education": 70
            },
            issues=[],
            suggestions=[],
            keyword_matches={},
            ats_compatibility=75
        )
        
        priorities = scorer.get_improvement_priority(result)
        
        assert len(priorities) >= 2
        # Projects (30) should be highest priority
        assert priorities[0]["category"] == "projects"
        assert priorities[0]["priority"] == "high"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
