"""Template service for LaTeX template operations."""

from typing import Optional, List, Dict
from uuid import UUID
from app.services.base import BaseService
from app.models.resume import Template, TemplateCreate, TemplateUpdate
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class TemplateService(BaseService):
    """Service for template-related operations."""
    
    def __init__(self):
        """Initialize template service."""
        super().__init__("templates")
    
    def get_public_templates(self, limit: int = 20, offset: int = 0) -> List[Template]:
        """Get public templates."""
        try:
            results = self.filter({"is_public": True}, limit, offset)
            return [Template(**template) for template in results]
        except Exception as e:
            logger.error(f"Error getting public templates: {e}")
            return []
    
    def get_featured_templates(self, limit: int = 10) -> List[Template]:
        """Get featured templates."""
        try:
            results = self.filter({"is_featured": True})
            return [Template(**template) for template in results[:limit]]
        except Exception as e:
            logger.error(f"Error getting featured templates: {e}")
            return []