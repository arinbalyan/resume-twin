"""API router aggregator."""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    health, auth, profiles, projects, templates, resume, ai, 
    education, experience, pdfs
)

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
api_router.include_router(education.router, prefix="/education", tags=["education"])
api_router.include_router(experience.router, prefix="/experience", tags=["experience"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
api_router.include_router(resume.router, prefix="/resume", tags=["resume"])
api_router.include_router(pdfs.router, prefix="/pdfs", tags=["pdf-storage"])
api_router.include_router(ai.router, tags=["ai-optimization"])