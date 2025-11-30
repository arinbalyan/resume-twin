"""Project portfolio models."""

from datetime import date
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


class ProjectBase(BaseModel):
    """Base project model."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    bullet_points: List[str] = Field(default_factory=list)
    category: str = Field(..., min_length=1)
    tags: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    github_url: Optional[str] = None
    live_url: Optional[str] = None
    demo_url: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str = Field(default="completed", pattern="^(draft|in_progress|completed|on_hold)$")
    is_featured: bool = False
    is_public: bool = False
    difficulty_level: Optional[int] = Field(None, ge=1, le=5)
    team_size: int = Field(default=1, ge=1)
    client_info: Optional[str] = None
    budget_range: Optional[str] = None
    impact_metrics: dict = Field(default_factory=dict)


class ProjectCreate(ProjectBase):
    """Project creation model."""
    pass


class ProjectUpdate(BaseModel):
    """Project update model."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    bullet_points: Optional[List[str]] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    technologies: Optional[List[str]] = None
    github_url: Optional[str] = None
    live_url: Optional[str] = None
    demo_url: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = Field(None, pattern="^(draft|in_progress|completed|on_hold)$")
    is_featured: Optional[bool] = None
    is_public: Optional[bool] = None
    difficulty_level: Optional[int] = Field(None, ge=1, le=5)
    team_size: Optional[int] = Field(None, ge=1)
    client_info: Optional[str] = None
    budget_range: Optional[str] = None
    impact_metrics: Optional[dict] = None

    @field_validator("end_date")
    @classmethod
    def validate_dates(cls, v: Optional[date], info) -> Optional[date]:
        if v and info.data.get("start_date") and v < info.data["start_date"]:
            raise ValueError("End date must be after start date")
        return v


class Project(ProjectBase):
    """Project model from database."""
    id: UUID
    user_id: UUID
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True


# Project Media Models
class ProjectMediaBase(BaseModel):
    """Base project media model."""
    file_url: str = Field(..., min_length=1)
    file_name: Optional[str] = None
    file_size: Optional[int] = Field(None, ge=0)
    media_type: Optional[str] = None
    caption: Optional[str] = None
    alt_text: Optional[str] = None
    display_order: int = Field(default=0, ge=0)
    is_cover_image: bool = False


class ProjectMediaCreate(ProjectMediaBase):
    """Project media creation model."""
    pass


class ProjectMediaUpdate(BaseModel):
    """Project media update model."""
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = Field(None, ge=0)
    media_type: Optional[str] = None
    caption: Optional[str] = None
    alt_text: Optional[str] = None
    display_order: Optional[int] = Field(None, ge=0)
    is_cover_image: Optional[bool] = None


class ProjectMedia(ProjectMediaBase):
    """Project media model from database."""
    id: UUID
    project_id: UUID
    created_at: date

    class Config:
        from_attributes = True


# Project Technology Models
class ProjectTechnologyBase(BaseModel):
    """Base project technology model."""
    technology_name: str = Field(..., min_length=1)
    technology_category: Optional[str] = None
    proficiency_level: Optional[int] = Field(None, ge=1, le=5)
    is_primary: bool = False


class ProjectTechnologyCreate(ProjectTechnologyBase):
    """Project technology creation model."""
    pass


class ProjectTechnologyUpdate(BaseModel):
    """Project technology update model."""
    technology_name: Optional[str] = None
    technology_category: Optional[str] = None
    proficiency_level: Optional[int] = Field(None, ge=1, le=5)
    is_primary: Optional[bool] = None


class ProjectTechnology(ProjectTechnologyBase):
    """Project technology model from database."""
    id: UUID
    project_id: UUID
    created_at: date

    class Config:
        from_attributes = True


# Complete Project with Relations
class ProjectWithMedia(Project):
    """Project with media and technologies."""
    media: List[ProjectMedia] = Field(default_factory=list)
    technologies: List[ProjectTechnology] = Field(default_factory=list)


class ProjectSummary(BaseModel):
    """Project summary for lists."""
    id: UUID
    title: str
    short_description: Optional[str]
    category: str
    tags: List[str]
    technologies: List[str]
    github_url: Optional[str]
    live_url: Optional[str]
    status: str
    is_featured: bool
    is_public: bool
    created_at: date
    media_count: int = 0
    technology_count: int = 0

    class Config:
        from_attributes = True


# Project Statistics
class ProjectStats(BaseModel):
    """Project statistics model."""
    total_projects: int = 0
    completed_projects: int = 0
    in_progress_projects: int = 0
    featured_projects: int = 0
    unique_technologies: List[str] = Field(default_factory=list)
    category_distribution: dict = Field(default_factory=dict)
    average_team_size: float = 0.0
    average_difficulty: float = 0.0


# Project Filtering and Search
class ProjectFilter(BaseModel):
    """Project filtering model."""
    category: Optional[str] = None
    status: Optional[str] = None
    is_featured: Optional[bool] = None
    tags: Optional[List[str]] = None
    technology: Optional[str] = None
    difficulty_level: Optional[int] = Field(None, ge=1, le=5)
    team_size: Optional[int] = Field(None, ge=1)
    start_date_from: Optional[date] = None
    start_date_to: Optional[date] = None
    end_date_from: Optional[date] = None
    end_date_to: Optional[date] = None


class ProjectSearch(BaseModel):
    """Project search model."""
    query: Optional[str] = None
    filters: Optional[ProjectFilter] = None
    sort_by: str = Field(default="created_at", pattern="^(title|created_at|updated_at|category|difficulty_level)$")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class ProjectSearchResult(BaseModel):
    """Project search result model."""
    projects: List[ProjectSummary]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool