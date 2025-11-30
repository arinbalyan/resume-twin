"""
Unit Tests for Project Service.

Tests cover:
- Project CRUD operations
- User project listing
- Project filtering and search
- Project data validation
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from uuid import uuid4, UUID
from datetime import date
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def sample_project_dict():
    """Create sample project data as dict for mocking database responses."""
    return {
        "id": uuid4(),
        "user_id": uuid4(),
        "title": "Test Project",
        "description": "A comprehensive test project",
        "short_description": "A test project",
        "bullet_points": ["Feature 1", "Feature 2"],
        "category": "web",
        "tags": ["python", "fastapi"],
        "technologies": ["Python", "FastAPI", "PostgreSQL"],
        "github_url": "https://github.com/user/project",
        "live_url": "https://project.example.com",
        "demo_url": None,
        "start_date": date(2024, 1, 1),
        "end_date": date(2024, 6, 30),
        "status": "completed",
        "is_featured": True,
        "is_public": True,
        "difficulty_level": 3,
        "team_size": 2,
        "client_info": None,
        "budget_range": None,
        "impact_metrics": {"users": 1000},
        "created_at": date.today(),
        "updated_at": date.today()
    }


@pytest.fixture
def mock_project_service():
    """Create mock project service."""
    with patch('app.services.project_service.BaseService.__init__', return_value=None):
        from app.services.project_service import ProjectService
        service = ProjectService()
        service.table_name = "projects"
        service.client = MagicMock()
        return service


# ============================================================================
# Project Service CRUD Tests
# ============================================================================

class TestProjectServiceCRUD:
    """Tests for Project Service CRUD operations."""
    
    def test_create_project_success(self, mock_project_service, sample_project_dict):
        """Should successfully create a project."""
        user_id = uuid4()
        
        mock_project_service.create = MagicMock(return_value=sample_project_dict)
        
        from app.models.projects import ProjectCreate
        project_create = ProjectCreate(
            title="Test Project",
            category="web",
            description="A test project"
        )
        
        result = mock_project_service.create_project(user_id, project_create)
        
        assert result is not None
        mock_project_service.create.assert_called_once()
    
    def test_create_project_failure(self, mock_project_service):
        """Should return None when creation fails."""
        user_id = uuid4()
        
        mock_project_service.create = MagicMock(side_effect=Exception("Database error"))
        
        from app.models.projects import ProjectCreate
        project_create = ProjectCreate(title="Test Project", category="web")
        
        result = mock_project_service.create_project(user_id, project_create)
        
        assert result is None
    
    def test_get_project_found(self, mock_project_service, sample_project_dict):
        """Should return project when found."""
        project_id = uuid4()
        
        mock_project_service.get_by_id = MagicMock(return_value=sample_project_dict)
        
        result = mock_project_service.get_project(project_id)
        
        assert result is not None
        assert result.title == "Test Project"
    
    def test_get_project_not_found(self, mock_project_service):
        """Should return None when project not found."""
        project_id = uuid4()
        
        mock_project_service.get_by_id = MagicMock(return_value=None)
        
        result = mock_project_service.get_project(project_id)
        
        assert result is None
    
    def test_update_project_success(self, mock_project_service, sample_project_dict):
        """Should successfully update project."""
        project_id = uuid4()
        
        updated_data = sample_project_dict.copy()
        updated_data["title"] = "Updated Project"
        
        mock_project_service.update = MagicMock(return_value=updated_data)
        
        from app.models.projects import ProjectUpdate
        project_update = ProjectUpdate(title="Updated Project")
        
        result = mock_project_service.update_project(project_id, project_update)
        
        assert result is not None
        mock_project_service.update.assert_called_once()
    
    def test_update_project_partial(self, mock_project_service, sample_project_dict):
        """Should update only specified fields."""
        project_id = uuid4()
        
        updated_data = sample_project_dict.copy()
        updated_data["is_featured"] = True
        
        mock_project_service.update = MagicMock(return_value=updated_data)
        
        from app.models.projects import ProjectUpdate
        project_update = ProjectUpdate(is_featured=True)
        
        result = mock_project_service.update_project(project_id, project_update)
        
        assert result is not None
    
    def test_update_project_failure(self, mock_project_service):
        """Should return None when update fails."""
        project_id = uuid4()
        
        mock_project_service.update = MagicMock(side_effect=Exception("Database error"))
        
        from app.models.projects import ProjectUpdate
        project_update = ProjectUpdate(title="Updated")
        
        result = mock_project_service.update_project(project_id, project_update)
        
        assert result is None
    
    def test_delete_project_success(self, mock_project_service):
        """Should successfully delete project."""
        project_id = uuid4()
        
        mock_project_service.delete = MagicMock(return_value=True)
        
        result = mock_project_service.delete_project(project_id)
        
        assert result is True
        mock_project_service.delete.assert_called_once_with(project_id)
    
    def test_delete_project_failure(self, mock_project_service):
        """Should return False when deletion fails."""
        project_id = uuid4()
        
        mock_project_service.delete = MagicMock(side_effect=Exception("Database error"))
        
        result = mock_project_service.delete_project(project_id)
        
        assert result is False


# ============================================================================
# User Projects Tests
# ============================================================================

class TestUserProjects:
    """Tests for user project listing."""
    
    def test_get_user_projects_with_results(self, mock_project_service, sample_project_dict):
        """Should return list of user projects."""
        user_id = uuid4()
        
        project1 = sample_project_dict.copy()
        project2 = sample_project_dict.copy()
        project2["id"] = uuid4()
        project2["title"] = "Second Project"
        
        mock_project_service.filter = MagicMock(return_value=[project1, project2])
        
        result = mock_project_service.get_user_projects(user_id)
        
        assert len(result) == 2
        mock_project_service.filter.assert_called_once()
    
    def test_get_user_projects_empty(self, mock_project_service):
        """Should return empty list when no projects."""
        user_id = uuid4()
        
        mock_project_service.filter = MagicMock(return_value=[])
        
        result = mock_project_service.get_user_projects(user_id)
        
        assert result == []
    
    def test_get_user_projects_pagination(self, mock_project_service, sample_project_dict):
        """Should support pagination."""
        user_id = uuid4()
        
        mock_project_service.filter = MagicMock(return_value=[sample_project_dict])
        
        mock_project_service.get_user_projects(user_id, limit=10, offset=20)
        
        mock_project_service.filter.assert_called_once()
    
    def test_get_user_projects_error_handling(self, mock_project_service):
        """Should handle errors gracefully."""
        user_id = uuid4()
        
        mock_project_service.filter = MagicMock(side_effect=Exception("Database error"))
        
        result = mock_project_service.get_user_projects(user_id)
        
        assert result == []


# ============================================================================
# Project Data Validation Tests
# ============================================================================

class TestProjectDataValidation:
    """Tests for project data validation."""
    
    def test_project_create_with_required_fields(self):
        """Should create project with required fields only."""
        from app.models.projects import ProjectCreate
        
        project = ProjectCreate(title="Test Project", category="web")
        
        assert project.title == "Test Project"
        assert project.category == "web"
        assert project.description is None
    
    def test_project_create_with_full_data(self):
        """Should create project with all fields."""
        from app.models.projects import ProjectCreate
        
        project = ProjectCreate(
            title="Full Project",
            category="web",
            description="Full description",
            technologies=["Python", "FastAPI"],
            tags=["ai", "web"],
            status="in_progress",
            is_featured=True,
            team_size=5
        )
        
        assert project.title == "Full Project"
        assert project.team_size == 5
        assert "Python" in project.technologies
    
    def test_project_update_partial(self):
        """Should allow partial updates."""
        from app.models.projects import ProjectUpdate
        
        update = ProjectUpdate(title="Updated Title")
        
        assert update.title == "Updated Title"
        assert update.description is None
        assert update.category is None
    
    def test_project_update_status_validation(self):
        """Should validate status values."""
        from app.models.projects import ProjectUpdate
        
        # Valid status
        update = ProjectUpdate(status="completed")
        assert update.status == "completed"
        
        # Invalid status should raise
        with pytest.raises(Exception):
            ProjectUpdate(status="invalid_status")


# ============================================================================
# Project Model Tests
# ============================================================================

class TestProjectModel:
    """Tests for Project Pydantic model."""
    
    def test_project_model_creation(self, sample_project_dict):
        """Should create valid Project model from dict."""
        from app.models.projects import Project
        
        project = Project(**sample_project_dict)
        
        assert project.title == "Test Project"
        assert project.category == "web"
        assert project.status == "completed"
    
    def test_project_model_with_defaults(self):
        """Should use default values where applicable."""
        from app.models.projects import Project
        
        minimal_data = {
            "id": uuid4(),
            "user_id": uuid4(),
            "title": "Test Project",
            "category": "web",
            "created_at": date.today(),
            "updated_at": date.today()
        }
        
        project = Project(**minimal_data)
        
        assert project.status == "completed"  # default
        assert project.team_size == 1  # default
        assert project.is_featured is False  # default


# ============================================================================
# Project Stats Tests
# ============================================================================

class TestProjectStats:
    """Tests for ProjectStats model."""
    
    def test_project_stats_defaults(self):
        """Should have correct default values."""
        from app.models.projects import ProjectStats
        
        stats = ProjectStats()
        
        assert stats.total_projects == 0
        assert stats.completed_projects == 0
        assert stats.unique_technologies == []
    
    def test_project_stats_with_data(self):
        """Should accept data correctly."""
        from app.models.projects import ProjectStats
        
        stats = ProjectStats(
            total_projects=10,
            completed_projects=8,
            in_progress_projects=2,
            featured_projects=3,
            unique_technologies=["Python", "JavaScript"],
            average_team_size=3.5
        )
        
        assert stats.total_projects == 10
        assert len(stats.unique_technologies) == 2


# ============================================================================
# Project Filter Tests
# ============================================================================

class TestProjectFilter:
    """Tests for ProjectFilter model."""
    
    def test_project_filter_empty(self):
        """Should allow empty filter."""
        from app.models.projects import ProjectFilter
        
        filter_obj = ProjectFilter()
        
        assert filter_obj.category is None
        assert filter_obj.status is None
    
    def test_project_filter_with_values(self):
        """Should accept filter values."""
        from app.models.projects import ProjectFilter
        
        filter_obj = ProjectFilter(
            category="web",
            status="completed",
            is_featured=True,
            tags=["python"]
        )
        
        assert filter_obj.category == "web"
        assert filter_obj.status == "completed"
        assert "python" in filter_obj.tags


# ============================================================================
# Project Search Tests
# ============================================================================

class TestProjectSearch:
    """Tests for ProjectSearch model."""
    
    def test_project_search_defaults(self):
        """Should have correct default values."""
        from app.models.projects import ProjectSearch
        
        search = ProjectSearch()
        
        assert search.query is None
        assert search.sort_by == "created_at"
        assert search.sort_order == "desc"
        assert search.page == 1
        assert search.page_size == 20
    
    def test_project_search_with_filter(self):
        """Should accept filter object."""
        from app.models.projects import ProjectSearch, ProjectFilter
        
        filter_obj = ProjectFilter(category="web")
        search = ProjectSearch(
            query="test",
            filters=filter_obj,
            page=2,
            page_size=10
        )
        
        assert search.query == "test"
        assert search.filters.category == "web"
        assert search.page == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
