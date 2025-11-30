"""PDF generation service for resumes."""

import os
from typing import Dict, Any, Optional, List
from pathlib import Path
from uuid import UUID
import logging
from datetime import datetime

from app.utils.logger import setup_logger
from app.services.pdf_generator_factory import pdf_generator, PdfGenerationMethod
from app.services.s3_service import s3_service
from app.services.supabase_service import supabase_service
from app.core.config import settings

logger = setup_logger(__name__)


class PDFService:
    """Service for generating PDF resumes."""
    
    def __init__(self):
        """Initialize PDF service."""
        logger.info(f"PDF service initialized with method: {settings.PDF_GENERATION_METHOD}")
    
    async def generate_resume_pdf(
        self,
        user_id: str,
        template_name: str,
        user_data: Dict[str, Any],
        selected_project_ids: Optional[List[str]] = None,
        selected_tags: Optional[List[str]] = None,
        output_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate PDF resume from template and user data."""
        try:
            logger.info(f"Generating resume PDF for user {user_id} using {settings.PDF_GENERATION_METHOD} method")
            
            # Prepare data with selected projects
            resume_data = await self._prepare_resume_data(
                user_id,
                user_data,
                selected_project_ids,
                selected_tags
            )
            
            # Generate output filename
            if not output_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_name = f"resume_{user_id}_{timestamp}"
            
            # Generate PDF using the factory (it will select the right method)
            pdf_bytes = pdf_generator.generate_resume_pdf(template_name, resume_data)
            
            if not pdf_bytes:
                raise Exception("PDF generation failed")
            
            # Upload to S3 (if configured)
            pdf_url = None
            if s3_service:
                try:
                    pdf_filename = f"{output_name}.pdf"
                    pdf_url = await s3_service.upload_file(
                        pdf_bytes,
                        pdf_filename,
                        content_type="application/pdf",
                        user_id=user_id
                    )
                    logger.info(f"PDF uploaded to S3: {pdf_url}")
                except Exception as e:
                    logger.warning(f"Failed to upload PDF to S3: {e}")
            
            return {
                "success": True,
                "pdf_content": pdf_bytes,
                "pdf_url": pdf_url,
                "filename": f"{output_name}.pdf",
                "size": len(pdf_bytes),
                "generation_method": settings.PDF_GENERATION_METHOD
            }
            
        except Exception as e:
            logger.error(f"Error generating resume PDF: {e}")
            raise
    
    async def _prepare_resume_data(
        self,
        user_id: str,
        user_data: Dict[str, Any],
        selected_project_ids: Optional[List[str]] = None,
        selected_tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Prepare resume data including filtered projects."""
        try:
            resume_data = user_data.copy()
            
            # Fetch user's projects
            projects_data = await supabase_service.get_user_projects(user_id)
            
            # Filter projects by IDs or tags
            filtered_projects = self._filter_projects(
                projects_data,
                selected_project_ids,
                selected_tags
            )
            
            # Format projects for LaTeX
            resume_data['projects'] = self._format_projects_for_latex(filtered_projects)
            
            # Extract and organize skills from projects
            resume_data['skills'] = self._extract_skills_from_projects(filtered_projects)
            
            return resume_data
            
        except Exception as e:
            logger.error(f"Error preparing resume data: {e}")
            return user_data
    
    def _filter_projects(
        self,
        projects: List[Dict[str, Any]],
        selected_ids: Optional[List[str]] = None,
        selected_tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Filter projects by IDs or tags."""
        if not projects:
            return []
        
        filtered = projects
        
        # Filter by IDs if provided
        if selected_ids:
            filtered = [p for p in filtered if p.get('id') in selected_ids]
        
        # Filter by tags if provided
        if selected_tags:
            filtered = [
                p for p in filtered
                if any(tag in p.get('tags', []) for tag in selected_tags)
            ]
        
        return filtered
    
    def _format_projects_for_latex(self, projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format projects for LaTeX template."""
        formatted = []
        
        for project in projects:
            formatted_project = {
                'title': project.get('title', ''),
                'short_description': project.get('short_description', ''),
                'description': project.get('description', ''),
                'bullet_points': project.get('bullet_points', []),
                'technologies': project.get('technologies', []),
                'github_url': project.get('github_url', ''),
                'live_url': project.get('live_url', ''),
                'start_date': self._format_date(project.get('start_date')),
                'end_date': self._format_date(project.get('end_date')),
                'tags': project.get('tags', [])
            }
            formatted.append(formatted_project)
        
        return formatted
    
    def _extract_skills_from_projects(self, projects: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Extract and categorize skills from projects."""
        skills = {
            'Programming Languages': set(),
            'Frameworks & Libraries': set(),
            'Tools & Technologies': set(),
            'Other': set()
        }
        
        # Common categorization
        languages = {'python', 'javascript', 'typescript', 'java', 'c++', 'c#', 'go', 'rust', 'ruby', 'php', 'swift', 'kotlin'}
        frameworks = {'react', 'vue', 'angular', 'django', 'flask', 'fastapi', 'express', 'nextjs', 'nuxt', 'spring', 'laravel'}
        tools = {'docker', 'kubernetes', 'aws', 'gcp', 'azure', 'git', 'jenkins', 'terraform', 'ansible'}
        
        for project in projects:
            technologies = project.get('technologies', [])
            for tech in technologies:
                tech_lower = tech.lower()
                if any(lang in tech_lower for lang in languages):
                    skills['Programming Languages'].add(tech)
                elif any(fw in tech_lower for fw in frameworks):
                    skills['Frameworks & Libraries'].add(tech)
                elif any(tool in tech_lower for tool in tools):
                    skills['Tools & Technologies'].add(tech)
                else:
                    skills['Other'].add(tech)
        
        # Convert sets to sorted lists
        return {k: sorted(list(v)) for k, v in skills.items() if v}
    
    def _format_date(self, date_str: Optional[str]) -> str:
        """Format date for LaTeX."""
        if not date_str:
            return ''
        
        try:
            # Try to parse and format date
            from dateutil import parser
            dt = parser.parse(date_str)
            return dt.strftime('%b %Y')
        except:
            return str(date_str)
    
    async def save_resume_version(
        self,
        user_id: str,
        template_id: str,
        title: str,
        latex_content: str,
        pdf_url: Optional[str],
        selected_project_ids: Optional[List[str]] = None,
        selected_tags: Optional[List[str]] = None,
        customizations: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Save resume version to database."""
        try:
            resume_version = {
                'user_id': user_id,
                'template_id': template_id,
                'title': title,
                'latex_content': latex_content,
                'pdf_url': pdf_url,
                'selected_project_ids': selected_project_ids or [],
                'selected_tags': selected_tags or [],
                'customizations': customizations or {},
                'status': 'completed',
                'created_at': datetime.utcnow().isoformat()
            }
            
            result = await supabase_service.create_resume_version(resume_version)
            return result
            
        except Exception as e:
            logger.error(f"Error saving resume version: {e}")
            raise
    
    def get_available_templates(self) -> List[Dict[str, str]]:
        """Get list of available templates for the current generation method."""
        try:
            # Get templates from the factory
            template_names = pdf_generator.get_available_templates()
            
            templates = []
            for name in template_names:
                templates.append({
                    'name': name,
                    'filename': f"{name}.{settings.PDF_GENERATION_METHOD}",
                    'method': settings.PDF_GENERATION_METHOD
                })
            
            return templates
            
        except Exception as e:
            logger.error(f"Error listing templates: {e}")
            return []
    
    def get_generation_method_status(self) -> Dict[str, Any]:
        """Get status of all PDF generation methods."""
        return pdf_generator.get_method_status()


# Global PDF service instance
pdf_service = PDFService()
