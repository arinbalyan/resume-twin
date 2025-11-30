"""User profile and education models."""

from datetime import date
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator


class ProfileBase(BaseModel):
    """Base profile model."""
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    other_links: dict = Field(default_factory=dict)
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    current_title: Optional[str] = None
    experience_years: int = Field(default=0, ge=0)
    preferred_job_types: List[str] = Field(default_factory=list)
    target_industries: List[str] = Field(default_factory=list)
    salary_expectation_min: Optional[int] = Field(None, ge=0)
    salary_expectation_max: Optional[int] = Field(None, ge=0)
    willing_to_relocate: bool = False
    is_public: bool = False


class ProfileCreate(ProfileBase):
    """Profile creation model."""
    pass


class ProfileUpdate(BaseModel):
    """Profile update model."""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    other_links: Optional[dict] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    current_title: Optional[str] = None
    experience_years: Optional[int] = Field(None, ge=0)
    preferred_job_types: Optional[List[str]] = None
    target_industries: Optional[List[str]] = None
    salary_expectation_min: Optional[int] = Field(None, ge=0)
    salary_expectation_max: Optional[int] = Field(None, ge=0)
    willing_to_relocate: Optional[bool] = None
    is_public: Optional[bool] = None

    @field_validator("salary_expectation_max")
    @classmethod
    def validate_salary_range(cls, v: Optional[int], info) -> Optional[int]:
        if v and info.data.get("salary_expectation_min") and v < info.data["salary_expectation_min"]:
            raise ValueError("Maximum salary must be greater than minimum salary")
        return v


class Profile(ProfileBase):
    """Profile model from database."""
    id: UUID
    profile_completion_score: int = Field(default=0, ge=0, le=100)
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True


# Education Models
class EducationBase(BaseModel):
    """Base education model."""
    institution: str = Field(..., min_length=1)
    degree: str = Field(..., min_length=1)
    field_of_study: Optional[str] = None
    cgpa: Optional[float] = Field(None, ge=0.0, le=10.0)
    percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    graduation_year: Optional[int] = Field(None, ge=1950, le=2030)
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    is_current: bool = False
    is_featured: bool = False

    @field_validator("graduation_year")
    @classmethod
    def validate_graduation_year(cls, v: Optional[int]) -> Optional[int]:
        from datetime import datetime
        current_year = datetime.now().year
        if v and (v < 1950 or v > current_year + 10):
            raise ValueError(f"Graduation year must be between 1950 and {current_year + 10}")
        return v

    @field_validator("end_date")
    @classmethod
    def validate_dates(cls, v: Optional[date], info) -> Optional[date]:
        if v and info.data.get("start_date") and v < info.data["start_date"]:
            raise ValueError("End date must be after start date")
        return v


class EducationCreate(EducationBase):
    """Education creation model."""
    pass


class EducationUpdate(BaseModel):
    """Education update model."""
    institution: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    cgpa: Optional[float] = Field(None, ge=0.0, le=10.0)
    percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    graduation_year: Optional[int] = Field(None, ge=1950, le=2030)
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    is_current: Optional[bool] = None
    is_featured: Optional[bool] = None


class Education(EducationBase):
    """Education model from database."""
    id: UUID
    user_id: UUID
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True


# Profile Statistics
class ProfileStats(BaseModel):
    """Profile statistics model."""
    total_projects: int = 0
    project_categories: int = 0
    unique_technologies: int = 0
    has_education: bool = False
    has_projects: bool = False
    has_experience: bool = False
    has_skills: bool = False
    has_resume: bool = False
    completion_percentage: int = 0

    @property
    def completion_score(self) -> int:
        """Calculate completion score."""
        score = 0
        score += 20 if self.has_education else 0
        score += 30 if self.has_projects else 0
        score += 20 if self.has_experience else 0
        score += 15 if self.has_skills else 0
        score += 15 if self.has_resume else 0
        return score