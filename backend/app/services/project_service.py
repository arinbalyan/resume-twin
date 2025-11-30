"""Project service for project operations."""

from typing import Optional, List, Dict, Any
from uuid import UUID
from app.services.base import BaseService
from app.models.projects import Project, ProjectCreate, ProjectUpdate, ProjectStats
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class ProjectService(BaseService):
    """Service for project-related operations."""
    
    def __init__(self):
        """Initialize project service."""
        super().__init__("projects")
    
    def create_project(self, user_id: UUID, project_data: ProjectCreate) -> Optional[Project]:
        """Create a new project."""
        project_dict = project_data.dict()
        project_dict["user_id"] = user_id
        
        try:
            result = self.create(project_dict)
            if result:
                return Project(**result)
            return None
        except Exception as e:
            logger.error(f"Error creating project for user {user_id}: {e}")
            return None
    
    def get_user_projects(self, user_id: UUID, limit: int = 50, offset: int = 0) -> List[Project]:
        """Get projects for a specific user."""
        try:
            results = self.filter({"user_id": str(user_id)}, limit, offset)
            return [Project(**project) for project in results]
        except Exception as e:
            logger.error(f"Error getting projects for user {user_id}: {e}")
            return []
    
    def get_project(self, project_id: UUID) -> Optional[Project]:
        """Get project by ID."""
        try:
            result = self.get_by_id(project_id)
            if result:
                return Project(**result)
            return None
        except Exception as e:
            logger.error(f"Error getting project {project_id}: {e}")
            return None
    
    def update_project(self, project_id: UUID, project_data: ProjectUpdate) -> Optional[Project]:
        """Update project data."""
        update_dict = project_data.dict(exclude_unset=True)
        
        try:
            result = self.update(project_id, update_dict)
            if result:
                return Project(**result)
            return None
        except Exception as e:
            logger.error(f"Error updating project {project_id}: {e}")
            return None
    
    def delete_project(self, project_id: UUID) -> bool:
        """Delete project."""
        try:
            return self.delete(project_id)
        except Exception as e:
            logger.error(f"Error deleting project {project_id}: {e}")
            return False