"""Professional experience models."""

from datetime import date
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


# Certification Models
class CertificationBase(BaseModel):
    """Base certification model."""
    name: str = Field(..., min_length=1)
    issuer: str = Field(..., min_length=1)
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    credential_id: Optional[str] = None
    verification_url: Optional[str] = None
    certificate_file_url: Optional[str] = None
    skills_acquired: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    is_verified: bool = False

    @field_validator("expiry_date")
    @classmethod
    def validate_expiry_date(cls, v: Optional[date], info) -> Optional[date]:
        if v and info.data.get("issue_date") and v < info.data["issue_date"]:
            raise ValueError("Expiry date must be after issue date")
        return v


class CertificationCreate(CertificationBase):
    """Certification creation model."""
    pass


class CertificationUpdate(BaseModel):
    """Certification update model."""
    name: Optional[str] = None
    issuer: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    credential_id: Optional[str] = None
    verification_url: Optional[str] = None
    certificate_file_url: Optional[str] = None
    skills_acquired: Optional[List[str]] = None
    description: Optional[str] = None
    is_verified: Optional[bool] = None


class Certification(CertificationBase):
    """Certification model from database."""
    id: UUID
    user_id: UUID
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True


# Internship Models
class InternshipBase(BaseModel):
    """Base internship model."""
    company: str = Field(..., min_length=1)
    role: str = Field(..., min_length=1)
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: bool = False
    description: Optional[str] = None
    achievements: List[str] = Field(default_factory=list)
    key_learnings: List[str] = Field(default_factory=list)
    team_size: Optional[int] = Field(None, ge=1)
    project_count: int = Field(default=0, ge=0)

    @field_validator("end_date")
    @classmethod
    def validate_dates(cls, v: Optional[date], info) -> Optional[date]:
        if v and info.data.get("start_date") and v < info.data["start_date"]:
            raise ValueError("End date must be after start date")
        return v


class InternshipCreate(InternshipBase):
    """Internship creation model."""
    pass


class InternshipUpdate(BaseModel):
    """Internship update model."""
    company: Optional[str] = None
    role: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: Optional[bool] = None
    description: Optional[str] = None
    achievements: Optional[List[str]] = None
    key_learnings: Optional[List[str]] = None
    team_size: Optional[int] = Field(None, ge=1)
    project_count: Optional[int] = Field(None, ge=0)


class Internship(InternshipBase):
    """Internship model from database."""
    id: UUID
    user_id: UUID
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True


# Course Models
class CourseBase(BaseModel):
    """Base course model."""
    name: str = Field(..., min_length=1)
    institution: Optional[str] = None
    instructor: Optional[str] = None
    completion_date: Optional[date] = None
    certificate_url: Optional[str] = None
    course_url: Optional[str] = None
    skills_acquired: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    duration_hours: Optional[int] = Field(None, ge=0)
    difficulty_level: Optional[int] = Field(None, ge=1, le=5)
    is_featured: bool = False


class CourseCreate(CourseBase):
    """Course creation model."""
    pass


class CourseUpdate(BaseModel):
    """Course update model."""
    name: Optional[str] = None
    institution: Optional[str] = None
    instructor: Optional[str] = None
    completion_date: Optional[date] = None
    certificate_url: Optional[str] = None
    course_url: Optional[str] = None
    skills_acquired: Optional[List[str]] = None
    description: Optional[str] = None
    duration_hours: Optional[int] = Field(None, ge=0)
    difficulty_level: Optional[int] = Field(None, ge=1, le=5)
    is_featured: Optional[bool] = None


class Course(CourseBase):
    """Course model from database."""
    id: UUID
    user_id: UUID
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True


# Activity Models
class ActivityBase(BaseModel):
    """Base activity model."""
    title: str = Field(..., min_length=1)
    organization: Optional[str] = None
    role: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: bool = False
    description: Optional[str] = None
    achievements: List[str] = Field(default_factory=list)
    activity_type: Optional[str] = None
    impact_scope: Optional[str] = Field(None, pattern="^(local|national|international)$")

    @field_validator("end_date")
    @classmethod
    def validate_dates(cls, v: Optional[date], info) -> Optional[date]:
        if v and info.data.get("start_date") and v < info.data["start_date"]:
            raise ValueError("End date must be after start date")
        return v


class ActivityCreate(ActivityBase):
    """Activity creation model."""
    pass


class ActivityUpdate(BaseModel):
    """Activity update model."""
    title: Optional[str] = None
    organization: Optional[str] = None
    role: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: Optional[bool] = None
    description: Optional[str] = None
    achievements: Optional[List[str]] = None
    activity_type: Optional[str] = None
    impact_scope: Optional[str] = Field(None, pattern="^(local|national|international)$")


class Activity(ActivityBase):
    """Activity model from database."""
    id: UUID
    user_id: UUID
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True


# Experience Summary Models
class ExperienceSummary(BaseModel):
    """Summary of all experience types for a user."""
    certifications: List[Certification]
    internships: List[Internship]
    courses: List[Course]
    activities: List[Activity]

    @property
    def total_experience_items(self) -> int:
        """Total number of experience items."""
        return len(self.certifications) + len(self.internships) + len(self.courses) + len(self.activities)

    @property
    def unique_skills_acquired(self) -> List[str]:
        """List of unique skills acquired across all experience."""
        skills = set()
        for cert in self.certifications:
            skills.update(cert.skills_acquired)
        for course in self.courses:
            skills.update(course.skills_acquired)
        return list(skills)


# Experience Statistics
class ExperienceStats(BaseModel):
    """Experience statistics model."""
    total_certifications: int = 0
    total_internships: int = 0
    total_courses: int = 0
    total_activities: int = 0
    unique_skills: List[str] = Field(default_factory=list)
    certification_issuers: List[str] = Field(default_factory=list)
    course_institutions: List[str] = Field(default_factory=list)
    activity_types: List[str] = Field(default_factory=list)
    average_course_difficulty: float = 0.0
    total_learning_hours: int = 0

    @property
    def total_items(self) -> int:
        """Total experience items."""
        return (self.total_certifications + self.total_internships + 
                self.total_courses + self.total_activities)

    @property
    def completion_rate(self) -> float:
        """Experience completion rate."""
        # This would be calculated based on expected vs actual items
        # For now, return a placeholder
        return 85.0