"""HTML-to-PDF service using WeasyPrint or fallback methods."""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from io import BytesIO

from jinja2 import Environment, FileSystemLoader, Template

from app.core.config import settings

logger = logging.getLogger(__name__)

# Try to import WeasyPrint, but handle gracefully if GTK libraries aren't available
WEASYPRINT_AVAILABLE = False
HTML = None
CSS = None
FontConfiguration = None

try:
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
    WEASYPRINT_AVAILABLE = True
    logger.info("WeasyPrint loaded successfully")
except OSError as e:
    logger.warning(f"WeasyPrint not available (missing GTK libraries): {e}")
    logger.warning("PDF generation will use fallback method. Install GTK for full WeasyPrint support:")
    logger.warning("  Windows: Install GTK3 from https://github.com/nickvdyck/weasyprint-windows/releases")
    logger.warning("  Or run: pip install weasyprint[test] and install GTK runtime")
except ImportError as e:
    logger.warning(f"WeasyPrint import failed: {e}")


# Sample resume data for template previews
SAMPLE_RESUME_DATA = {
    "user_name": "Alex Johnson",
    "title": "Senior Full Stack Developer",
    "email": "alex.johnson@email.com",
    "phone": "+1 (555) 123-4567",
    "location": "San Francisco, CA",
    "linkedin": "https://linkedin.com/in/alexjohnson",
    "github": "https://github.com/alexjohnson",
    "github_username": "alexjohnson",
    "website": "https://alexjohnson.dev",
    "years_experience": "8+",
    
    "summary": "Passionate full-stack developer with 8+ years of experience building scalable web applications. Expertise in React, Node.js, Python, and cloud technologies. Led teams of 5-10 engineers and delivered products serving millions of users. Strong advocate for clean code, test-driven development, and agile methodologies.",
    
    "skills": {
        "Programming Languages": ["Python", "JavaScript", "TypeScript", "Go", "SQL"],
        "Frameworks & Libraries": ["React", "Next.js", "FastAPI", "Django", "Node.js", "Express"],
        "Databases & Tools": ["PostgreSQL", "MongoDB", "Redis", "Docker", "Kubernetes", "AWS"]
    },
    
    "experience": [
        {
            "position": "Senior Full Stack Developer",
            "company": "TechCorp Inc.",
            "location": "San Francisco, CA",
            "start_date": "Jan 2021",
            "end_date": None,
            "achievements": [
                "Led the development of a microservices architecture serving 2M+ daily active users",
                "Reduced API response times by 60% through caching strategies and database optimization",
                "Mentored a team of 5 junior developers, establishing code review practices",
                "Implemented CI/CD pipelines reducing deployment time from 2 hours to 15 minutes"
            ]
        },
        {
            "position": "Full Stack Developer",
            "company": "StartupXYZ",
            "location": "New York, NY",
            "start_date": "Jun 2018",
            "end_date": "Dec 2020",
            "achievements": [
                "Built the core product from scratch using React and Python FastAPI",
                "Designed and implemented a real-time notification system using WebSockets",
                "Integrated third-party payment systems processing $1M+ monthly transactions",
                "Collaborated with UX team to improve user engagement by 40%"
            ]
        },
        {
            "position": "Junior Developer",
            "company": "WebAgency",
            "location": "Boston, MA",
            "start_date": "Aug 2016",
            "end_date": "May 2018",
            "achievements": [
                "Developed responsive web applications for 20+ clients across various industries",
                "Created reusable component library reducing development time by 30%",
                "Maintained legacy PHP applications while transitioning to modern stack"
            ]
        }
    ],
    
    "projects": [
        {
            "title": "E-commerce Platform",
            "description": "A scalable e-commerce platform with real-time inventory management",
            "bullet_points": [
                "Built with Next.js, FastAPI, and PostgreSQL with Redis caching",
                "Handles 10,000+ concurrent users with 99.9% uptime",
                "Integrated Stripe payments and automated order fulfillment",
                "Implemented AI-powered product recommendations increasing sales by 25%"
            ],
            "technologies": ["Next.js", "FastAPI", "PostgreSQL", "Redis", "Stripe", "AWS"],
            "github_url": "https://github.com/alexjohnson/ecommerce-platform",
            "live_url": "https://myecommerce.demo",
            "start_date": "Mar 2023",
            "end_date": None,
            "tags": ["fullstack", "ecommerce", "ai"]
        },
        {
            "title": "Real-time Collaboration Tool",
            "description": "Google Docs-like collaborative editing platform",
            "bullet_points": [
                "Implemented CRDT-based conflict resolution for simultaneous editing",
                "WebSocket architecture supporting 500+ concurrent editors",
                "Rich text editor with markdown support and file attachments"
            ],
            "technologies": ["React", "Node.js", "Socket.io", "MongoDB", "Docker"],
            "github_url": "https://github.com/alexjohnson/collab-editor",
            "live_url": None,
            "start_date": "Aug 2022",
            "end_date": "Feb 2023",
            "tags": ["realtime", "collaboration"]
        },
        {
            "title": "DevOps Dashboard",
            "description": "Centralized monitoring and deployment management dashboard",
            "bullet_points": [
                "Unified view of CI/CD pipelines, server health, and logs",
                "Custom alerting system with Slack and email integration",
                "Automated rollback capabilities for failed deployments"
            ],
            "technologies": ["Vue.js", "Go", "Prometheus", "Grafana", "Kubernetes"],
            "github_url": "https://github.com/alexjohnson/devops-dashboard",
            "live_url": None,
            "start_date": "Jan 2022",
            "end_date": "Jul 2022",
            "tags": ["devops", "monitoring"]
        }
    ],
    
    "education": [
        {
            "degree": "Master of Science in Computer Science",
            "institution": "Stanford University",
            "start_date": "2014",
            "end_date": "2016",
            "gpa": "3.8"
        },
        {
            "degree": "Bachelor of Science in Software Engineering",
            "institution": "MIT",
            "start_date": "2010",
            "end_date": "2014",
            "gpa": "3.7"
        }
    ],
    
    "certifications": [
        {
            "name": "AWS Solutions Architect Professional",
            "issuer": "Amazon Web Services",
            "date": "2023"
        },
        {
            "name": "Google Cloud Professional Data Engineer",
            "issuer": "Google Cloud",
            "date": "2022"
        },
        {
            "name": "Certified Kubernetes Administrator",
            "issuer": "CNCF",
            "date": "2022"
        }
    ],
    
    "languages": [
        {"name": "English", "level": "Native"},
        {"name": "Spanish", "level": "Professional"},
        {"name": "French", "level": "Conversational"}
    ],
    
    "activities": [
        "Open source contributor to React and FastAPI",
        "Technical blog with 10,000+ monthly readers",
        "Speaker at PyCon and ReactConf",
        "Volunteer coding instructor at local community center"
    ]
}


class HtmlToPdfService:
    """Service for generating PDFs from HTML templates using WeasyPrint or cloud fallback."""

    def __init__(self):
        """Initialize the HTML-to-PDF service."""
        self.templates_dir = Path(settings.TEMPLATES_DIR) / "html"
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Font configuration for WeasyPrint (only if available)
        self.font_config = FontConfiguration() if WEASYPRINT_AVAILABLE else None
        self.weasyprint_available = WEASYPRINT_AVAILABLE
        
        # Import cloud PDF service for fallback
        from app.services.cloud_pdf_service import cloud_pdf_service
        self.cloud_pdf_service = cloud_pdf_service
        
        if WEASYPRINT_AVAILABLE:
            logger.info(f"HTML-to-PDF service initialized with WeasyPrint. Templates: {self.templates_dir}")
        elif self.cloud_pdf_service.is_available():
            logger.info(f"HTML-to-PDF service using cloud provider: {self.cloud_pdf_service.provider}. Templates: {self.templates_dir}")
        else:
            logger.warning(f"HTML-to-PDF service initialized WITHOUT PDF generation. Configure a cloud provider or install WeasyPrint. Templates: {self.templates_dir}")

    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render HTML template with context.

        Args:
            template_name: Name of the template file
            context: Template context variables

        Returns:
            Rendered HTML string

        Raises:
            FileNotFoundError: If template doesn't exist
            Exception: If template rendering fails
        """
        try:
            template = self.jinja_env.get_template(template_name)
            html_content = template.render(**context)
            logger.info(f"Template '{template_name}' rendered successfully")
            return html_content
        except Exception as e:
            logger.error(f"Failed to render template '{template_name}': {str(e)}")
            raise

    async def generate_pdf(
        self,
        template_name: str,
        context: Dict[str, Any],
        custom_css: Optional[str] = None
    ) -> bytes:
        """
        Generate PDF from HTML template.
        Uses WeasyPrint if available, otherwise falls back to cloud service.

        Args:
            template_name: Name of the HTML template file
            context: Template context variables
            custom_css: Optional custom CSS to apply

        Returns:
            PDF file as bytes

        Raises:
            Exception: If PDF generation fails
        """
        # Render HTML template first
        html_content = self.render_template(template_name, context)
        if custom_css:
            # Inject custom CSS into the HTML
            html_content = html_content.replace('</head>', f'<style>{custom_css}</style></head>')
        
        # Try WeasyPrint first (local, fastest)
        if self.weasyprint_available:
            try:
                html = HTML(string=html_content, base_url=str(self.templates_dir))
                css_list = []
                if custom_css:
                    css_list.append(CSS(string=custom_css, font_config=self.font_config))
                
                pdf_bytes = html.write_pdf(
                    stylesheets=css_list if css_list else None,
                    font_config=self.font_config
                )
                logger.info(f"PDF generated with WeasyPrint from '{template_name}' ({len(pdf_bytes)} bytes)")
                return pdf_bytes
            except Exception as e:
                logger.warning(f"WeasyPrint failed, trying cloud fallback: {e}")
        
        # Try cloud PDF service as fallback
        if self.cloud_pdf_service.is_available():
            try:
                pdf_bytes = await self.cloud_pdf_service.generate_pdf_from_html(html_content)
                logger.info(f"PDF generated with cloud service from '{template_name}' ({len(pdf_bytes)} bytes)")
                return pdf_bytes
            except Exception as e:
                logger.error(f"Cloud PDF service failed: {e}")
                raise RuntimeError(f"Cloud PDF generation failed: {e}")
        
        # No PDF generation available
        error_msg = (
            "No PDF generation method available. Options:\n"
            "1. Install GTK3 for WeasyPrint (local)\n"
            "2. Add PDFSHIFT_API_KEY to .env (free: 250 PDFs/month at pdfshift.io)\n"
            "3. Add HTML2PDF_API_KEY to .env (free tier at html2pdf.app)\n"
            "4. Add BROWSERLESS_API_KEY to .env (free: 1000 calls/month at browserless.io)"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    async def generate_pdf_from_html_async(
        self,
        html_content: str,
        custom_css: Optional[str] = None
    ) -> bytes:
        """
        Generate PDF directly from HTML string (async version with cloud fallback).

        Args:
            html_content: HTML content as string
            custom_css: Optional custom CSS to apply

        Returns:
            PDF file as bytes

        Raises:
            Exception: If PDF generation fails
        """
        if custom_css:
            html_content = html_content.replace('</head>', f'<style>{custom_css}</style></head>')
        
        # Try WeasyPrint first
        if self.weasyprint_available:
            try:
                html = HTML(string=html_content)
                pdf_bytes = html.write_pdf(font_config=self.font_config)
                logger.info(f"PDF generated with WeasyPrint ({len(pdf_bytes)} bytes)")
                return pdf_bytes
            except Exception as e:
                logger.warning(f"WeasyPrint failed: {e}")
        
        # Try cloud PDF service
        if self.cloud_pdf_service.is_available():
            pdf_bytes = await self.cloud_pdf_service.generate_pdf_from_html(html_content)
            logger.info(f"PDF generated with cloud service ({len(pdf_bytes)} bytes)")
            return pdf_bytes
        
        raise RuntimeError("No PDF generation method available")

    def validate_template_exists(self, template_name: str) -> bool:
        """
        Check if template file exists.

        Args:
            template_name: Name of the template file

        Returns:
            True if template exists, False otherwise
        """
        template_path = self.templates_dir / template_name
        return template_path.exists() and template_path.is_file()

    def list_available_templates(self) -> list[str]:
        """
        List all available HTML templates.

        Returns:
            List of template filenames
        """
        if not self.templates_dir.exists():
            return []
        
        templates = [
            f.name for f in self.templates_dir.iterdir()
            if f.is_file() and f.suffix in ['.html', '.htm']
        ]
        
        logger.info(f"Found {len(templates)} HTML templates")
        return sorted(templates)

    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """
        Get information about a specific template.

        Args:
            template_name: Name of the template file

        Returns:
            Dictionary with template information
        """
        template_path = self.templates_dir / template_name
        
        if not template_path.exists():
            return None
        
        # Read template content to extract metadata
        content = template_path.read_text(encoding='utf-8')
        
        # Extract title from HTML
        import re
        title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
        title = title_match.group(1) if title_match else template_name
        
        # Determine template style based on name
        style_map = {
            'professional': 'Professional - Classic single-column layout',
            'modern': 'Modern - Two-column with sidebar skills',
            'minimal': 'Minimal - Clean typography-focused design',
            'creative': 'Creative - Colorful sidebar with visual elements',
            'developer': 'Developer - GitHub-inspired dark theme'
        }
        
        base_name = template_name.replace('.html', '').replace('_resume', '')
        description = style_map.get(base_name, 'Custom template')
        
        return {
            'name': template_name,
            'display_name': base_name.replace('_', ' ').title(),
            'description': description,
            'path': str(template_path),
            'size': template_path.stat().st_size
        }

    def list_templates_with_info(self) -> List[Dict[str, Any]]:
        """
        List all templates with their metadata.

        Returns:
            List of template info dictionaries
        """
        templates = self.list_available_templates()
        return [
            self.get_template_info(t) for t in templates
            if self.get_template_info(t) is not None
        ]

    def is_pdf_generation_available(self) -> bool:
        """Check if PDF generation is available (WeasyPrint or cloud)."""
        return self.weasyprint_available or self.cloud_pdf_service.is_available()

    def get_status(self) -> Dict[str, Any]:
        """Get service status including PDF generation availability."""
        cloud_status = self.cloud_pdf_service.get_status()
        
        if self.weasyprint_available:
            method = "weasyprint"
            message = "WeasyPrint is ready for PDF generation (local)"
        elif self.cloud_pdf_service.is_available():
            method = f"cloud ({cloud_status['provider']})"
            message = f"Using cloud PDF service: {cloud_status['provider']}"
        else:
            method = "none"
            message = "No PDF method available. Get a free API key from pdfshift.io"
        
        return {
            "pdf_available": self.is_pdf_generation_available(),
            "method": method,
            "weasyprint_available": self.weasyprint_available,
            "cloud_pdf": cloud_status,
            "templates_dir": str(self.templates_dir),
            "templates_count": len(self.list_available_templates()),
            "message": message
        }

    async def preview_template(self, template_name: str, custom_data: Optional[Dict[str, Any]] = None) -> bytes:
        """
        Generate a preview PDF using sample data.

        Args:
            template_name: Name of the template file
            custom_data: Optional custom data to merge with sample data

        Returns:
            PDF bytes for preview
            
        Raises:
            RuntimeError: If no PDF generation available
        """
        # Merge sample data with any custom overrides
        preview_data = SAMPLE_RESUME_DATA.copy()
        if custom_data:
            preview_data.update(custom_data)
        
        return await self.generate_pdf(template_name, preview_data)

    def render_template_html(self, template_name: str, custom_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Render template HTML for preview (without PDF conversion).

        Args:
            template_name: Name of the template file
            custom_data: Optional custom data to merge with sample data

        Returns:
            Rendered HTML string
        """
        preview_data = SAMPLE_RESUME_DATA.copy()
        if custom_data:
            preview_data.update(custom_data)
        
        return self.render_template(template_name, preview_data)

    def get_sample_data(self) -> Dict[str, Any]:
        """Get sample resume data for testing templates."""
        return SAMPLE_RESUME_DATA.copy()


# Global instance
html_to_pdf_service = HtmlToPdfService()
