"""
Unit Tests for Profile Service.

Tests cover:
- Profile creation
- Profile retrieval
- Profile updates
- Profile deletion
- Public profile listing
- Profile search
- Location-based queries
- Profile statistics
- Profile completion scoring
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
def sample_profile_dict():
    """Create sample profile data as dict for mocking database responses."""
    return {
        "id": uuid4(),
        "email": "john@example.com",
        "full_name": "John Doe",
        "phone": "+1234567890",
        "city": "San Francisco",
        "country": "USA",
        "linkedin_url": "https://linkedin.com/in/johndoe",
        "github_url": "https://github.com/johndoe",
        "portfolio_url": "https://johndoe.dev",
        "other_links": {},
        "avatar_url": None,
        "bio": "Experienced developer",
        "current_title": "Software Engineer",
        "experience_years": 5,
        "preferred_job_types": ["full-time", "contract"],
        "target_industries": ["technology", "finance"],
        "salary_expectation_min": 100000,
        "salary_expectation_max": 150000,
        "willing_to_relocate": True,
        "is_public": False,
        "profile_completion_score": 75,
        "created_at": date.today(),
        "updated_at": date.today()
    }


@pytest.fixture
def mock_profile_service():
    """Create mock profile service."""
    with patch('app.services.profile_service.BaseService.__init__', return_value=None):
        from app.services.profile_service import ProfileService
        service = ProfileService()
        service.table_name = "profiles"
        service.client = MagicMock()
        return service


# ============================================================================
# Profile Service CRUD Tests
# ============================================================================

class TestProfileServiceCRUD:
    """Tests for Profile Service CRUD operations."""
    
    def test_create_profile_success(self, mock_profile_service, sample_profile_dict):
        """Should successfully create a profile."""
        user_id = uuid4()
        
        mock_profile_service.create = MagicMock(return_value=sample_profile_dict)
        
        from app.models.user import ProfileCreate
        profile_create = ProfileCreate(
            email="john@example.com",
            full_name="John Doe",
            current_title="Software Engineer"
        )
        
        result = mock_profile_service.create_profile(user_id, profile_create)
        
        assert result is not None
        mock_profile_service.create.assert_called_once()
    
    def test_create_profile_failure(self, mock_profile_service):
        """Should return None when creation fails."""
        user_id = uuid4()
        
        mock_profile_service.create = MagicMock(side_effect=Exception("Database error"))
        
        from app.models.user import ProfileCreate
        profile_create = ProfileCreate(
            email="john@example.com",
            full_name="John Doe"
        )
        
        result = mock_profile_service.create_profile(user_id, profile_create)
        
        assert result is None
    
    def test_get_profile_found(self, mock_profile_service, sample_profile_dict):
        """Should return profile when found."""
        user_id = uuid4()
        
        mock_profile_service.get_by_id = MagicMock(return_value=sample_profile_dict)
        
        result = mock_profile_service.get_profile(user_id)
        
        assert result is not None
        assert result.full_name == "John Doe"
    
    def test_get_profile_not_found(self, mock_profile_service):
        """Should return None when profile not found."""
        user_id = uuid4()
        
        mock_profile_service.get_by_id = MagicMock(return_value=None)
        
        result = mock_profile_service.get_profile(user_id)
        
        assert result is None
    
    def test_update_profile_success(self, mock_profile_service, sample_profile_dict):
        """Should successfully update profile."""
        user_id = uuid4()
        
        updated_data = sample_profile_dict.copy()
        updated_data["current_title"] = "Senior Software Engineer"
        
        mock_profile_service.update = MagicMock(return_value=updated_data)
        
        from app.models.user import ProfileUpdate
        profile_update = ProfileUpdate(current_title="Senior Software Engineer")
        
        result = mock_profile_service.update_profile(user_id, profile_update)
        
        assert result is not None
        mock_profile_service.update.assert_called_once()
    
    def test_delete_profile_success(self, mock_profile_service):
        """Should successfully delete profile."""
        user_id = uuid4()
        
        mock_profile_service.delete = MagicMock(return_value=True)
        
        result = mock_profile_service.delete_profile(user_id)
        
        assert result is True
        mock_profile_service.delete.assert_called_once_with(user_id)
    
    def test_delete_profile_failure(self, mock_profile_service):
        """Should return False when deletion fails."""
        user_id = uuid4()
        
        mock_profile_service.delete = MagicMock(side_effect=Exception("Database error"))
        
        result = mock_profile_service.delete_profile(user_id)
        
        assert result is False


# ============================================================================
# Public Profile Tests
# ============================================================================

class TestPublicProfiles:
    """Tests for public profile listing."""
    
    def test_get_public_profiles_with_results(self, mock_profile_service, sample_profile_dict):
        """Should return list of public profiles."""
        sample_profile_dict["is_public"] = True
        
        mock_profile_service.filter = MagicMock(return_value=[sample_profile_dict])
        
        result = mock_profile_service.get_public_profiles(limit=20, offset=0)
        
        assert len(result) == 1
        mock_profile_service.filter.assert_called_once_with({"is_public": True}, 20, 0)
    
    def test_get_public_profiles_empty(self, mock_profile_service):
        """Should return empty list when no public profiles."""
        mock_profile_service.filter = MagicMock(return_value=[])
        
        result = mock_profile_service.get_public_profiles()
        
        assert result == []
    
    def test_get_public_profiles_pagination(self, mock_profile_service, sample_profile_dict):
        """Should support pagination."""
        mock_profile_service.filter = MagicMock(return_value=[sample_profile_dict])
        
        mock_profile_service.get_public_profiles(limit=10, offset=20)
        
        mock_profile_service.filter.assert_called_once_with({"is_public": True}, 10, 20)


# ============================================================================
# Profile Search Tests
# ============================================================================

class TestProfileSearch:
    """Tests for profile search functionality."""
    
    def test_search_profiles_by_name(self, mock_profile_service, sample_profile_dict):
        """Should search profiles by name."""
        mock_profile_service.search = MagicMock(return_value=[sample_profile_dict])
        
        result = mock_profile_service.search_profiles("John", limit=20)
        
        assert len(result) == 1
        mock_profile_service.search.assert_called_once_with(
            "John", 
            ["full_name", "current_title", "bio"]
        )
    
    def test_search_profiles_no_results(self, mock_profile_service):
        """Should return empty list when no matches."""
        mock_profile_service.search = MagicMock(return_value=[])
        
        result = mock_profile_service.search_profiles("NonexistentPerson")
        
        assert result == []
    
    def test_search_profiles_pagination(self, mock_profile_service, sample_profile_dict):
        """Should apply pagination to search results."""
        profiles = [sample_profile_dict.copy() for _ in range(30)]
        mock_profile_service.search = MagicMock(return_value=profiles)
        
        result = mock_profile_service.search_profiles("engineer", limit=10, offset=5)
        
        assert len(result) == 10


# ============================================================================
# Location-Based Query Tests
# ============================================================================

class TestLocationBasedQueries:
    """Tests for location-based profile queries."""
    
    def test_get_profiles_by_city(self, mock_profile_service, sample_profile_dict):
        """Should filter profiles by city."""
        mock_profile_service.filter = MagicMock(return_value=[sample_profile_dict])
        
        result = mock_profile_service.get_profiles_by_location(city="San Francisco")
        
        assert len(result) == 1
        mock_profile_service.filter.assert_called_once_with({"city": "San Francisco"})
    
    def test_get_profiles_by_country(self, mock_profile_service, sample_profile_dict):
        """Should filter profiles by country."""
        mock_profile_service.filter = MagicMock(return_value=[sample_profile_dict])
        
        result = mock_profile_service.get_profiles_by_location(country="USA")
        
        mock_profile_service.filter.assert_called_once_with({"country": "USA"})
    
    def test_get_profiles_by_city_and_country(self, mock_profile_service, sample_profile_dict):
        """Should filter profiles by both city and country."""
        mock_profile_service.filter = MagicMock(return_value=[sample_profile_dict])
        
        result = mock_profile_service.get_profiles_by_location(
            city="San Francisco",
            country="USA"
        )
        
        mock_profile_service.filter.assert_called_once_with({
            "city": "San Francisco",
            "country": "USA"
        })
    
    def test_get_profiles_by_title(self, mock_profile_service, sample_profile_dict):
        """Should filter profiles by job title."""
        mock_profile_service.filter = MagicMock(return_value=[sample_profile_dict])
        
        result = mock_profile_service.get_profiles_by_title("Software Engineer")
        
        mock_profile_service.filter.assert_called_once_with(
            {"current_title": "Software Engineer"}, 
            20
        )


# ============================================================================
# Profile Statistics Tests
# ============================================================================

class TestProfileStatistics:
    """Tests for profile statistics."""
    
    def test_get_profile_stats_returns_stats_object(self, mock_profile_service):
        """Should return ProfileStats object."""
        user_id = uuid4()
        
        result = mock_profile_service.get_profile_stats(user_id)
        
        from app.models.user import ProfileStats
        assert isinstance(result, ProfileStats)
    
    def test_get_profile_stats_default_values(self, mock_profile_service):
        """Should return default values for stats."""
        user_id = uuid4()
        
        result = mock_profile_service.get_profile_stats(user_id)
        
        assert result.total_projects == 0
        assert result.completion_percentage == 0


# ============================================================================
# Profile Completion Score Tests
# ============================================================================

class TestProfileCompletionScore:
    """Tests for profile completion score calculation."""
    
    def test_update_completion_score_complete_profile(self, mock_profile_service, sample_profile_dict):
        """Should calculate high score for complete profile."""
        user_id = uuid4()
        
        # Create a complete profile data
        complete_profile_data = sample_profile_dict.copy()
        complete_profile_data.update({
            "avatar_url": "https://example.com/avatar.jpg",
            "preferred_job_types": ["full-time"],
            "target_industries": ["technology"]
        })
        
        from app.models.user import Profile
        mock_profile = Profile(**complete_profile_data)
        
        mock_profile_service.get_profile = MagicMock(return_value=mock_profile)
        mock_profile_service.update = MagicMock(return_value={"profile_completion_score": 90})
        
        result = mock_profile_service.update_profile_completion_score(user_id)
        
        assert result is True
        mock_profile_service.update.assert_called_once()
    
    def test_update_completion_score_profile_not_found(self, mock_profile_service):
        """Should return False when profile not found."""
        user_id = uuid4()
        
        mock_profile_service.get_profile = MagicMock(return_value=None)
        
        result = mock_profile_service.update_profile_completion_score(user_id)
        
        assert result is False


# ============================================================================
# Featured and Recent Profiles Tests
# ============================================================================

class TestFeaturedAndRecentProfiles:
    """Tests for featured and recent profile retrieval."""
    
    def test_get_featured_profiles(self, mock_profile_service, sample_profile_dict):
        """Should return profiles sorted by completion score."""
        profile1 = sample_profile_dict.copy()
        profile1["profile_completion_score"] = 90
        
        profile2 = sample_profile_dict.copy()
        profile2["id"] = uuid4()
        profile2["profile_completion_score"] = 70
        
        profile3 = sample_profile_dict.copy()
        profile3["id"] = uuid4()
        profile3["profile_completion_score"] = 85
        
        profiles = [profile1, profile2, profile3]
        
        mock_profile_service.filter = MagicMock(return_value=profiles)
        
        result = mock_profile_service.get_featured_profiles(limit=10)
        
        assert len(result) == 3
        # Should be sorted by completion score descending
        assert result[0].profile_completion_score >= result[1].profile_completion_score
    
    def test_get_recent_profiles(self, mock_profile_service, sample_profile_dict):
        """Should return recently created profiles."""
        mock_profile_service.filter = MagicMock(return_value=[sample_profile_dict])
        
        result = mock_profile_service.get_recent_profiles(limit=10)
        
        assert len(result) == 1
        mock_profile_service.filter.assert_called_once_with({"is_public": True})


# ============================================================================
# Profile Model Tests
# ============================================================================

class TestProfileModels:
    """Tests for Profile Pydantic models."""
    
    def test_profile_create_with_required_fields(self):
        """Should create ProfileCreate with required fields."""
        from app.models.user import ProfileCreate
        
        profile = ProfileCreate(email="test@example.com")
        
        assert profile.email == "test@example.com"
        assert profile.full_name is None
    
    def test_profile_create_with_all_fields(self):
        """Should create ProfileCreate with all fields."""
        from app.models.user import ProfileCreate
        
        profile = ProfileCreate(
            email="test@example.com",
            full_name="Test User",
            phone="+1234567890",
            city="New York",
            country="USA",
            current_title="Developer",
            bio="Test bio",
            experience_years=5,
            is_public=True
        )
        
        assert profile.email == "test@example.com"
        assert profile.full_name == "Test User"
        assert profile.experience_years == 5
    
    def test_profile_update_partial(self):
        """Should allow partial updates."""
        from app.models.user import ProfileUpdate
        
        update = ProfileUpdate(full_name="Updated Name")
        
        assert update.full_name == "Updated Name"
        assert update.city is None
    
    def test_profile_stats_defaults(self):
        """Should have correct default values."""
        from app.models.user import ProfileStats
        
        stats = ProfileStats()
        
        assert stats.total_projects == 0
        assert stats.has_education is False
        assert stats.completion_percentage == 0
    
    def test_profile_stats_completion_score(self):
        """Should calculate completion score correctly."""
        from app.models.user import ProfileStats
        
        stats = ProfileStats(
            has_education=True,
            has_projects=True,
            has_experience=True,
            has_skills=True,
            has_resume=True
        )
        
        # 20 + 30 + 20 + 15 + 15 = 100
        assert stats.completion_score == 100
    
    def test_profile_stats_partial_completion(self):
        """Should calculate partial completion score."""
        from app.models.user import ProfileStats
        
        stats = ProfileStats(
            has_education=True,  # 20
            has_projects=True,   # 30
            has_experience=False,
            has_skills=True,     # 15
            has_resume=False
        )
        
        # 20 + 30 + 15 = 65
        assert stats.completion_score == 65


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
