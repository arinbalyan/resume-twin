"""
Unit Tests for Template Service.

Tests cover:
- Public template retrieval
- Featured template retrieval
- Template filtering
- Template model validation
"""

import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from datetime import date
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


def make_sample_template():
    """Create sample template data as dict."""
    return {
        "id": uuid4(),
        "name": "Modern Resume",
        "category": "professional",
        "subcategory": "tech",
        "description": "A clean, modern resume template",
        "latex_content": "\\documentclass{article}\\begin{document}...\\end{document}",
        "css_styles": None,
        "preview_image_url": "https://example.com/preview.png",
        "thumbnail_url": "https://example.com/thumb.png",
        "is_public": True,
        "is_featured": True,
        "tags": ["modern", "clean", "professional"],
        "compatibility": {"latex": True, "pdf": True},
        "customization_options": {"font_size": [10, 11, 12]},
        "download_count": 100,
        "rating": 4.5,
        "rating_count": 25,
        "created_by": uuid4(),
        "created_at": date.today(),
        "updated_at": date.today()
    }


@pytest.fixture
def sample_template_dict():
    """Fixture for sample template data."""
    return make_sample_template()


@pytest.fixture
def mock_template_service():
    """Create mock template service."""
    with patch('app.services.template_service.BaseService.__init__', return_value=None):
        from app.services.template_service import TemplateService
        service = TemplateService()
        service.table_name = "templates"
        service.client = MagicMock()
        return service


class TestTemplateService:
    """Tests for Template Service operations."""
    
    def test_get_public_templates(self, mock_template_service, sample_template_dict):
        """Should return list of public templates."""
        mock_template_service.filter = MagicMock(return_value=[sample_template_dict])
        
        result = mock_template_service.get_public_templates(limit=20, offset=0)
        
        assert len(result) == 1
        mock_template_service.filter.assert_called_once_with({"is_public": True}, 20, 0)
    
    def test_get_public_templates_empty(self, mock_template_service):
        """Should return empty list when no public templates."""
        mock_template_service.filter = MagicMock(return_value=[])
        
        result = mock_template_service.get_public_templates()
        
        assert result == []
    
    def test_get_public_templates_error(self, mock_template_service):
        """Should handle errors gracefully."""
        mock_template_service.filter = MagicMock(side_effect=Exception("Database error"))
        
        result = mock_template_service.get_public_templates()
        
        assert result == []
    
    def test_get_featured_templates(self, mock_template_service, sample_template_dict):
        """Should return featured templates."""
        mock_template_service.filter = MagicMock(return_value=[sample_template_dict])
        
        result = mock_template_service.get_featured_templates(limit=10)
        
        assert len(result) == 1
        mock_template_service.filter.assert_called_once_with({"is_featured": True})
    
    def test_get_featured_templates_respects_limit(self, mock_template_service):
        """Should respect limit parameter."""
        templates = [make_sample_template() for _ in range(20)]
        mock_template_service.filter = MagicMock(return_value=templates)
        
        result = mock_template_service.get_featured_templates(limit=5)
        
        assert len(result) == 5
    
    def test_get_featured_templates_error(self, mock_template_service):
        """Should handle errors gracefully."""
        mock_template_service.filter = MagicMock(side_effect=Exception("Database error"))
        
        result = mock_template_service.get_featured_templates()
        
        assert result == []
    
    def test_get_template_by_id_found(self, mock_template_service, sample_template_dict):
        """Should return template when found."""
        template_id = uuid4()
        mock_template_service.get_by_id = MagicMock(return_value=sample_template_dict)
        
        result = mock_template_service.get_by_id(template_id)
        
        assert result is not None
        assert result["name"] == "Modern Resume"
    
    def test_get_template_by_id_not_found(self, mock_template_service):
        """Should return None when template not found."""
        template_id = uuid4()
        mock_template_service.get_by_id = MagicMock(return_value=None)
        
        result = mock_template_service.get_by_id(template_id)
        
        assert result is None


class TestTemplateModel:
    """Tests for Template Pydantic model."""
    
    def test_template_create_minimal(self):
        """Should create template with required fields."""
        from app.models.resume import TemplateCreate
        
        template = TemplateCreate(
            name="Basic Template",
            category="simple",
            latex_content="\\documentclass{article}"
        )
        
        assert template.name == "Basic Template"
        assert template.is_public is True
    
    def test_template_create_full(self):
        """Should create template with all fields."""
        from app.models.resume import TemplateCreate
        
        template = TemplateCreate(
            name="Full Template",
            category="professional",
            subcategory="software",
            description="A complete template",
            latex_content="\\documentclass{article}",
            is_featured=True,
            tags=["professional", "modern"]
        )
        
        assert template.is_featured is True
        assert "professional" in template.tags
    
    def test_template_update_partial(self):
        """Should allow partial updates."""
        from app.models.resume import TemplateUpdate
        
        update = TemplateUpdate(name="Updated Name")
        
        assert update.name == "Updated Name"
        assert update.category is None
    
    def test_template_model_from_dict(self, sample_template_dict):
        """Should create Template model from dict."""
        from app.models.resume import Template
        
        template = Template(**sample_template_dict)
        
        assert template.name == "Modern Resume"
        assert template.rating == 4.5


class TestTemplateRating:
    """Tests for template rating models."""
    
    def test_template_rating_create(self):
        """Should create rating with required fields."""
        from app.models.resume import TemplateRatingCreate
        
        rating = TemplateRatingCreate(rating=5)
        
        assert rating.rating == 5
        assert rating.review is None
    
    def test_template_rating_with_review(self):
        """Should create rating with review."""
        from app.models.resume import TemplateRatingCreate
        
        rating = TemplateRatingCreate(
            rating=4,
            review="Great template, very professional!",
            is_featured_review=True
        )
        
        assert rating.rating == 4
        assert rating.is_featured_review is True
    
    def test_template_rating_validation(self):
        """Should validate rating range."""
        from app.models.resume import TemplateRatingCreate
        
        for r in [1, 2, 3, 4, 5]:
            rating = TemplateRatingCreate(rating=r)
            assert rating.rating == r
        
        with pytest.raises(Exception):
            TemplateRatingCreate(rating=0)
        
        with pytest.raises(Exception):
            TemplateRatingCreate(rating=6)


class TestTemplateSearch:
    """Tests for template search model."""
    
    def test_template_search_defaults(self):
        """Should have correct default values."""
        from app.models.resume import TemplateSearch
        
        search = TemplateSearch()
        
        assert search.query is None
        assert search.sort_by == "created_at"
        assert search.sort_order == "desc"
        assert search.page == 1
        assert search.page_size == 20
    
    def test_template_search_with_filters(self):
        """Should accept search parameters."""
        from app.models.resume import TemplateSearch
        
        search = TemplateSearch(
            query="modern resume",
            category="professional",
            is_featured=True,
            min_rating=4.0,
            page=2
        )
        
        assert search.query == "modern resume"
        assert search.category == "professional"
        assert search.min_rating == 4.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
