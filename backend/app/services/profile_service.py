"""Profile service for user profile operations."""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from app.services.base import BaseService
from app.models.user import Profile, ProfileCreate, ProfileUpdate, ProfileStats
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class ProfileService(BaseService):
    """Service for profile-related operations."""
    
    def __init__(self):
        """Initialize profile service."""
        super().__init__("profiles")
    
    def create_profile(self, user_id: UUID, profile_data: ProfileCreate) -> Optional[Profile]:
        """Create a new profile."""
        profile_dict = profile_data.dict()
        profile_dict["id"] = user_id
        
        try:
            result = self.create(profile_dict)
            if result:
                return Profile(**result)
            return None
        except Exception as e:
            logger.error(f"Error creating profile for user {user_id}: {e}")
            return None
    
    def get_profile(self, user_id: UUID) -> Optional[Profile]:
        """Get profile by user ID."""
        try:
            result = self.get_by_id(user_id)
            if result:
                return Profile(**result)
            return None
        except Exception as e:
            logger.error(f"Error getting profile for user {user_id}: {e}")
            return None
    
    def update_profile(self, user_id: UUID, profile_data: ProfileUpdate) -> Optional[Profile]:
        """Update profile data."""
        update_dict = profile_data.dict(exclude_unset=True)
        update_dict["updated_at"] = datetime.utcnow()
        
        try:
            result = self.update(user_id, update_dict)
            if result:
                return Profile(**result)
            return None
        except Exception as e:
            logger.error(f"Error updating profile for user {user_id}: {e}")
            return None
    
    def delete_profile(self, user_id: UUID) -> bool:
        """Delete profile (and related data via CASCADE)."""
        try:
            return self.delete(user_id)
        except Exception as e:
            logger.error(f"Error deleting profile for user {user_id}: {e}")
            return False
    
    def get_public_profiles(self, limit: int = 20, offset: int = 0) -> List[Profile]:
        """Get public profiles for browsing."""
        try:
            result = self.filter({"is_public": True}, limit, offset)
            return [Profile(**profile) for profile in result]
        except Exception as e:
            logger.error(f"Error getting public profiles: {e}")
            return []
    
    def search_profiles(self, query: str, limit: int = 20, offset: int = 0) -> List[Profile]:
        """Search profiles by name, title, or bio."""
        try:
            results = self.search(query, ["full_name", "current_title", "bio"])
            return [Profile(**profile) for profile in results[offset:offset + limit]]
        except Exception as e:
            logger.error(f"Error searching profiles with query '{query}': {e}")
            return []
    
    def get_profiles_by_location(self, city: str = None, country: str = None) -> List[Profile]:
        """Get profiles by location."""
        filters = {}
        if city:
            filters["city"] = city
        if country:
            filters["country"] = country
        
        try:
            results = self.filter(filters)
            return [Profile(**profile) for profile in results]
        except Exception as e:
            logger.error(f"Error getting profiles by location: {e}")
            return []
    
    def get_profiles_by_title(self, title: str, limit: int = 20) -> List[Profile]:
        """Get profiles by current job title."""
        try:
            results = self.filter({"current_title": title}, limit)
            return [Profile(**profile) for profile in results]
        except Exception as e:
            logger.error(f"Error getting profiles by title '{title}': {e}")
            return []
    
    def get_profile_stats(self, user_id: UUID) -> ProfileStats:
        """Calculate comprehensive profile statistics."""
        try:
            # This would typically involve joins or separate queries
            # For now, return basic stats structure
            return ProfileStats(
                total_projects=0,
                project_categories=0,
                unique_technologies=0,
                has_education=False,
                has_projects=False,
                has_experience=False,
                has_skills=False,
                has_resume=False,
                completion_percentage=0
            )
        except Exception as e:
            logger.error(f"Error calculating profile stats for user {user_id}: {e}")
            return ProfileStats()
    
    def update_profile_completion_score(self, user_id: UUID) -> bool:
        """Update profile completion score based on filled fields."""
        try:
            profile = self.get_profile(user_id)
            if not profile:
                return False
            
            score = 0
            # Calculate completion score based on filled fields
            if profile.full_name: score += 10
            if profile.bio: score += 10
            if profile.current_title: score += 10
            if profile.avatar_url: score += 10
            if profile.linkedin_url or profile.github_url: score += 10
            if profile.city and profile.country: score += 10
            if profile.experience_years > 0: score += 10
            if profile.preferred_job_types: score += 10
            if profile.target_industries: score += 10
            
            # Update the score
            return bool(self.update(user_id, {"profile_completion_score": score}))
        except Exception as e:
            logger.error(f"Error updating completion score for user {user_id}: {e}")
            return False
    
    def get_featured_profiles(self, limit: int = 10) -> List[Profile]:
        """Get featured profiles (high completion score and public)."""
        try:
            # This would typically use a more complex query with sorting
            results = self.filter({"is_public": True})
            # Sort by completion score (would need proper database sorting)
            featured = sorted(results, key=lambda x: x.get("profile_completion_score", 0), reverse=True)
            return [Profile(**profile) for profile in featured[:limit]]
        except Exception as e:
            logger.error(f"Error getting featured profiles: {e}")
            return []
    
    def get_recent_profiles(self, limit: int = 10) -> List[Profile]:
        """Get recently created public profiles."""
        try:
            results = self.filter({"is_public": True})
            # Sort by creation date (would need proper database sorting)
            recent = sorted(results, key=lambda x: x.get("created_at", ""), reverse=True)
            return [Profile(**profile) for profile in recent[:limit]]
        except Exception as e:
            logger.error(f"Error getting recent profiles: {e}")
            return []