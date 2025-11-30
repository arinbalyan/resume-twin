"""Resume service for resume operations."""

from typing import Optional, List, Dict, Any
from uuid import UUID
from app.services.base import BaseService
from app.models.resume import ResumeVersion, ResumeVersionCreate, ResumeVersionUpdate
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class ResumeService(BaseService):
    """Service for resume-related operations."""
    
    def __init__(self):
        """Initialize resume service."""
        super().__init__("resume_versions")
    
    def create_resume(self, user_id: UUID, template_id: UUID, resume_data: ResumeVersionCreate) -> Optional[ResumeVersion]:
        """Create a new resume version."""
        resume_dict = resume_data.dict()
        resume_dict["user_id"] = user_id
        resume_dict["template_id"] = template_id
        
        try:
            result = self.create(resume_dict)
            if result:
                return ResumeVersion(**result)
            return None
        except Exception as e:
            logger.error(f"Error creating resume for user {user_id}: {e}")
            return None