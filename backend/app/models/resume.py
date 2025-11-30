"""Resume generation and template models."""

from datetime import date
from typing import Optional, List, Dict
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


# Template Models
class TemplateBase(BaseModel):
    """Base template model."""
    name: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., min_length=1)
    subcategory: Optional[str] = None
    description: Optional[str] = None
    latex_content: str = Field(..., min_length=1)
    css_styles: Optional[str] = None
    preview_image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    is_public: bool = True
    is_featured: bool = False
    tags: List[str] = Field(default_factory=list)
    compatibility: Dict = Field(default_factory=dict)
    customization_options: Dict = Field(default_factory=dict)


class TemplateCreate(TemplateBase):
    """Template creation model."""
    pass


class TemplateUpdate(BaseModel):
    """Template update model."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[str] = None
    subcategory: Optional[str] = None
    description: Optional[str] = None
    latex_content: Optional[str] = None
    css_styles: Optional[str] = None
    preview_image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    is_public: Optional[bool] = None
    is_featured: Optional[bool] = None
    tags: Optional[List[str]] = None
    compatibility: Optional[Dict] = None
    customization_options: Optional[Dict] = None


class Template(TemplateBase):
    """Template model from database."""
    id: UUID
    download_count: int = 0
    rating: float = 0.0
    rating_count: int = 0
    created_by: Optional[UUID] = None
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True


# Template Rating Models
class TemplateRatingBase(BaseModel):
    """Base template rating model."""
    rating: int = Field(..., ge=1, le=5)
    review: Optional[str] = None
    is_featured_review: bool = False


class TemplateRatingCreate(TemplateRatingBase):
    """Template rating creation model."""
    pass


class TemplateRatingUpdate(BaseModel):
    """Template rating update model."""
    rating: Optional[int] = Field(None, ge=1, le=5)
    review: Optional[str] = None
    is_featured_review: Optional[bool] = None


class TemplateRating(TemplateRatingBase):
    """Template rating model from database."""
    id: UUID
    template_id: UUID
    user_id: UUID
    created_at: date

    class Config:
        from_attributes = True


# Resume Version Models
class ResumeVersionBase(BaseModel):
    """Base resume version model."""
    title: str = Field(..., min_length=1, max_length=100)
    job_description: Optional[str] = None
    optimized_content: Optional[Dict] = None
    latex_content: Optional[str] = None
    pdf_url: Optional[str] = None
    preview_url: Optional[str] = None
    is_ai_optimized: bool = False
    optimization_score: Optional[int] = Field(None, ge=0, le=100)
    optimization_version: int = 1
    sections_included: List[str] = Field(default_factory=list)
    customizations: Dict = Field(default_factory=dict)
    status: str = Field(default="draft", pattern="^(draft|generating|ready|error)$")
    is_default: bool = False
    is_public: bool = False


class ResumeVersionCreate(ResumeVersionBase):
    """Resume version creation model."""
    pass


class ResumeVersionUpdate(BaseModel):
    """Resume version update model."""
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    job_description: Optional[str] = None
    optimized_content: Optional[Dict] = None
    latex_content: Optional[str] = None
    pdf_url: Optional[str] = None
    preview_url: Optional[str] = None
    is_ai_optimized: Optional[bool] = None
    optimization_score: Optional[int] = Field(None, ge=0, le=100)
    optimization_version: Optional[int] = Field(None, ge=1)
    sections_included: Optional[List[str]] = None
    customizations: Optional[Dict] = None
    status: Optional[str] = Field(None, pattern="^(draft|generating|ready|error)$")
    is_default: Optional[bool] = None
    is_public: Optional[bool] = None


class ResumeVersion(ResumeVersionBase):
    """Resume version model from database."""
    id: UUID
    user_id: UUID
    template_id: Optional[UUID] = None
    download_count: int = 0
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True


# Optimization History Models
class OptimizationHistoryBase(BaseModel):
    """Base optimization history model."""
    job_description: str = Field(..., min_length=1)
    keywords_extracted: Optional[Dict] = None
    optimization_applied: Optional[Dict] = None
    before_score: Optional[int] = Field(None, ge=0, le=100)
    after_score: Optional[int] = Field(None, ge=0, le=100)
    optimization_type: Optional[str] = Field(None, pattern="^(keyword|content|format|full)$")
    ai_model_version: Optional[str] = None
    processing_time_ms: Optional[int] = Field(None, ge=0)


class OptimizationHistoryCreate(OptimizationHistoryBase):
    """Optimization history creation model."""
    pass


class OptimizationHistory(OptimizationHistoryBase):
    """Optimization history model from database."""
    id: UUID
    resume_version_id: UUID
    created_at: date

    class Config:
        from_attributes = True


# Template Statistics and Summary Models
class TemplateStats(BaseModel):
    """Template statistics model."""
    total_templates: int = 0
    public_templates: int = 0
    featured_templates: int = 0
    category_distribution: Dict = Field(default_factory=dict)
    average_rating: float = 0.0
    total_downloads: int = 0
    top_rated_templates: List[Template] = Field(default_factory=list)
    most_downloaded_templates: List[Template] = Field(default_factory=list)


class TemplateSearch(BaseModel):
    """Template search and filtering model."""
    query: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    is_featured: Optional[bool] = None
    tags: Optional[List[str]] = None
    min_rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    sort_by: str = Field(default="created_at", pattern="^(name|created_at|rating|download_count)$")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class TemplateSearchResult(BaseModel):
    """Template search result model."""
    templates: List[Template]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


# Resume Generation Models
class ResumeGenerationRequest(BaseModel):
    """Resume generation request model."""
    template_id: UUID
    user_id: UUID
    sections_to_include: List[str] = Field(default_factory=list)
    job_description: Optional[str] = None
    customizations: Dict = Field(default_factory=dict)
    force_regenerate: bool = False


class ResumeGenerationResponse(BaseModel):
    """Resume generation response model."""
    resume_version_id: UUID
    status: str
    pdf_url: Optional[str] = None
    preview_url: Optional[str] = None
    optimization_score: Optional[int] = None
    error_message: Optional[str] = None
    processing_time_ms: Optional[int] = None


# AI Optimization Models
class AIOptimizationRequest(BaseModel):
    """AI optimization request model."""
    resume_content: Dict
    job_description: str
    optimization_type: str = Field(default="full", pattern="^(keyword|content|format|full)$")
    ai_model: str = Field(default="gpt-3.5-turbo")


class AIOptimizationResponse(BaseModel):
    """AI optimization response model."""
    optimized_content: Dict
    optimization_score: int
    keywords_added: List[str]
    keywords_removed: List[str]
    content_improvements: List[str]
    processing_time_ms: int
    ai_model_used: str


class KeywordAnalysis(BaseModel):
    """Keyword analysis model."""
    keywords_found: List[str]
    keywords_suggested: List[str]
    industry_specific_terms: List[str]
    action_words: List[str]
    technical_skills: List[str]
    soft_skills: List[str]
    missing_keywords: List[str]