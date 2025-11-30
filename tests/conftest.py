"""
Pytest configuration and shared fixtures for all tests.

This module contains:
- Common fixtures for mocking services
- Sample data factories
- Test database configuration
- Async test configuration
"""

import pytest
import asyncio
from typing import Dict, Any, List, Generator
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from unittest.mock import MagicMock, AsyncMock, patch
import sys
import os

# Add backend to path for imports
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Configure pytest-asyncio
pytest_plugins = ('pytest_asyncio',)


# ============================================================================
# Async Test Configuration
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Sample Data Factories
# ============================================================================

@pytest.fixture
def sample_user_id() -> UUID:
    """Generate a sample user ID."""
    return uuid4()


@pytest.fixture
def sample_profile_data() -> Dict[str, Any]:
    """Generate sample profile data."""
    return {
        "id": str(uuid4()),
        "full_name": "John Doe",
        "email": "john.doe@example.com",
        "current_title": "Senior Software Engineer",
        "bio": "Experienced developer with 10+ years in full-stack development",
        "city": "San Francisco",
        "country": "USA",
        "linkedin_url": "https://linkedin.com/in/johndoe",
        "github_url": "https://github.com/johndoe",
        "experience_years": 10,
        "is_public": True,
        "profile_completion_score": 85,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }


@pytest.fixture
def sample_project_data() -> Dict[str, Any]:
    """Generate sample project data."""
    return {
        "id": str(uuid4()),
        "user_id": str(uuid4()),
        "title": "Resume Twin Platform",
        "short_description": "AI-powered resume generation platform",
        "description": "A comprehensive platform for creating optimized resumes using AI",
        "technologies": ["Python", "FastAPI", "React", "TypeScript", "Supabase"],
        "bullet_points": [
            "Built AI-powered resume optimization engine",
            "Implemented real-time collaboration features",
            "Achieved 95% ATS compatibility score"
        ],
        "github_url": "https://github.com/user/resume-twin",
        "live_url": "https://resume-twin.com",
        "tags": ["ai", "resume", "career"],
        "is_featured": True,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }


@pytest.fixture
def sample_job_description() -> str:
    """Generate sample job description."""
    return """
    Senior Software Engineer - Full Stack
    
    Company: TechCorp Inc.
    Location: San Francisco, CA (Remote Available)
    
    About the Role:
    We are looking for a Senior Software Engineer to join our growing team.
    You will work on building scalable web applications using modern technologies.
    
    Requirements:
    - 5+ years of experience in software development
    - Strong proficiency in Python and JavaScript/TypeScript
    - Experience with React, Vue, or Angular
    - Familiarity with cloud platforms (AWS, GCP, or Azure)
    - Experience with databases (PostgreSQL, MongoDB)
    - Strong understanding of REST APIs and microservices
    - Excellent problem-solving and communication skills
    
    Nice to Have:
    - Experience with Docker and Kubernetes
    - Knowledge of CI/CD pipelines
    - Contributions to open-source projects
    
    Responsibilities:
    - Design and implement new features
    - Write clean, maintainable code
    - Participate in code reviews
    - Mentor junior developers
    - Collaborate with product and design teams
    """


@pytest.fixture
def sample_resume_data() -> Dict[str, Any]:
    """Generate sample resume data for scoring."""
    return {
        "user_name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+1-555-123-4567",
        "linkedin": "https://linkedin.com/in/johndoe",
        "github": "https://github.com/johndoe",
        "location": "San Francisco, CA",
        "summary": "Senior Software Engineer with 10+ years of experience building scalable web applications. Led teams of 5+ engineers, achieving 40% improvement in system performance. Expert in Python, JavaScript, and cloud technologies.",
        "skills": {
            "Programming Languages": ["Python", "JavaScript", "TypeScript", "Go"],
            "Frameworks": ["React", "FastAPI", "Django", "Node.js"],
            "Databases": ["PostgreSQL", "MongoDB", "Redis"],
            "Cloud & DevOps": ["AWS", "Docker", "Kubernetes", "Terraform"]
        },
        "experience": [
            {
                "position": "Senior Software Engineer",
                "company": "TechCorp Inc.",
                "duration": "2020-Present",
                "achievements": [
                    "Led development of microservices architecture serving 1M+ users",
                    "Reduced API response time by 60% through optimization",
                    "Mentored team of 5 junior developers"
                ]
            },
            {
                "position": "Software Engineer",
                "company": "StartupXYZ",
                "duration": "2017-2020",
                "achievements": [
                    "Built real-time notification system using WebSockets",
                    "Implemented CI/CD pipeline reducing deployment time by 70%",
                    "Developed RESTful APIs for mobile applications"
                ]
            }
        ],
        "projects": [
            {
                "title": "Open Source Analytics Tool",
                "description": "Built analytics dashboard for tracking user behavior",
                "technologies": ["React", "Python", "PostgreSQL"],
                "github_url": "https://github.com/johndoe/analytics",
                "bullet_points": ["500+ GitHub stars", "Used by 50+ companies"]
            }
        ],
        "education": [
            {
                "degree": "Bachelor of Science in Computer Science",
                "institution": "Stanford University",
                "year": "2017",
                "gpa": "3.8"
            }
        ],
        "certifications": [
            "AWS Solutions Architect Professional",
            "Google Cloud Professional Developer"
        ]
    }


@pytest.fixture
def sample_file_data() -> Dict[str, Any]:
    """Generate sample file upload data."""
    return {
        "id": str(uuid4()),
        "user_id": str(uuid4()),
        "original_filename": "resume.pdf",
        "file_size": 1024 * 100,  # 100KB
        "mime_type": "application/pdf",
        "file_category": "resume",
        "file_path": f"uploads/{uuid4()}/resume.pdf",
        "upload_status": "completed",
        "virus_scan_status": "clean",
        "processing_status": "completed",
        "expires_at": (datetime.utcnow() + timedelta(days=365)).isoformat(),
        "created_at": datetime.utcnow().isoformat()
    }


@pytest.fixture
def sample_github_profile() -> Dict[str, Any]:
    """Generate sample GitHub profile data."""
    return {
        "username": "johndoe",
        "name": "John Doe",
        "email": "john@example.com",
        "bio": "Full-stack developer passionate about open source",
        "company": "TechCorp",
        "location": "San Francisco, CA",
        "blog": "https://johndoe.dev",
        "twitter_username": "johndoe",
        "avatar_url": "https://avatars.githubusercontent.com/u/12345",
        "profile_url": "https://github.com/johndoe",
        "public_repos": 50,
        "public_gists": 10,
        "followers": 500,
        "following": 100,
        "created_at": "2015-01-15T00:00:00Z",
        "hireable": True
    }


@pytest.fixture
def sample_github_repos() -> List[Dict[str, Any]]:
    """Generate sample GitHub repository data."""
    return [
        {
            "name": "awesome-project",
            "full_name": "johndoe/awesome-project",
            "description": "An awesome project for doing awesome things",
            "url": "https://github.com/johndoe/awesome-project",
            "homepage": "https://awesome-project.com",
            "language": "Python",
            "topics": ["python", "api", "web"],
            "stars": 150,
            "forks": 25,
            "watchers": 150,
            "open_issues": 5,
            "is_fork": False,
            "is_archived": False,
            "created_at": "2022-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "pushed_at": "2024-01-01T00:00:00Z",
            "default_branch": "main",
            "license": "MIT"
        },
        {
            "name": "react-components",
            "full_name": "johndoe/react-components",
            "description": "Reusable React component library",
            "url": "https://github.com/johndoe/react-components",
            "homepage": None,
            "language": "TypeScript",
            "topics": ["react", "typescript", "ui"],
            "stars": 75,
            "forks": 10,
            "watchers": 75,
            "open_issues": 2,
            "is_fork": False,
            "is_archived": False,
            "created_at": "2023-03-01T00:00:00Z",
            "updated_at": "2024-02-01T00:00:00Z",
            "pushed_at": "2024-02-01T00:00:00Z",
            "default_branch": "main",
            "license": "MIT"
        }
    ]


# ============================================================================
# Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_supabase_client():
    """Create a mock Supabase client."""
    mock = MagicMock()
    mock.table.return_value.insert.return_value.execute.return_value.data = [{"id": str(uuid4())}]
    mock.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
    mock.table.return_value.update.return_value.eq.return_value.execute.return_value.data = []
    mock.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = []
    return mock


@pytest.fixture
def mock_s3_client():
    """Create a mock S3 client."""
    mock = MagicMock()
    mock.put_object.return_value = {}
    mock.get_object.return_value = {"Body": MagicMock(read=lambda: b"test content")}
    mock.delete_object.return_value = {}
    mock.head_object.return_value = {
        "ContentLength": 1024,
        "LastModified": datetime.utcnow(),
        "ContentType": "application/pdf",
        "ETag": '"abc123"',
        "Metadata": {}
    }
    mock.generate_presigned_url.return_value = "https://s3.amazonaws.com/bucket/file?signed=true"
    return mock


@pytest.fixture
def mock_httpx_client():
    """Create a mock httpx async client."""
    mock = AsyncMock()
    mock.get.return_value.status_code = 200
    mock.get.return_value.json.return_value = {}
    mock.post.return_value.status_code = 200
    mock.post.return_value.json.return_value = {}
    return mock


# ============================================================================
# Test Environment Configuration
# ============================================================================

@pytest.fixture(autouse=True)
def mock_environment_variables(monkeypatch):
    """Set up mock environment variables for testing."""
    monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "test-key")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "test-service-key")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-openrouter-key")
    monkeypatch.setenv("AI_MODEL", "test-model")
    monkeypatch.setenv("S3_BUCKET_NAME", "test-bucket")
    monkeypatch.setenv("S3_ACCESS_KEY", "test-access-key")
    monkeypatch.setenv("S3_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("S3_REGION", "us-east-1")
    monkeypatch.setenv("GITHUB_TOKEN", "test-github-token")
    monkeypatch.setenv("PDF_GENERATION_METHOD", "html")


# ============================================================================
# Utility Functions
# ============================================================================

def create_mock_response(data: Any, status_code: int = 200) -> MagicMock:
    """Create a mock HTTP response."""
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = data
    response.text = str(data)
    return response


def create_async_mock_response(data: Any, status_code: int = 200) -> AsyncMock:
    """Create an async mock HTTP response."""
    response = AsyncMock()
    response.status_code = status_code
    response.json = MagicMock(return_value=data)
    response.text = str(data)
    return response
