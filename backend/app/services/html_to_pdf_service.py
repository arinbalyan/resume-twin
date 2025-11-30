"""HTML-to-PDF service using WeasyPrint."""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from io import BytesIO

from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from jinja2 import Environment, FileSystemLoader, Template

from app.core.config import settings

logger = logging.getLogger(__name__)


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
    """Service for generating PDFs from HTML templates using WeasyPrint."""

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
        
        # Font configuration for WeasyPrint
        self.font_config = FontConfiguration()
        
        logger.info(f"HTML-to-PDF service initialized with templates directory: {self.templates_dir}")

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

    def generate_pdf(
        self,
        template_name: str,
        context: Dict[str, Any],
        custom_css: Optional[str] = None
    ) -> bytes:
        """
        Generate PDF from HTML template.

        Args:
            template_name: Name of the HTML template file
            context: Template context variables
            custom_css: Optional custom CSS to apply

        Returns:
            PDF file as bytes

        Raises:
            Exception: If PDF generation fails
        """
        try:
            # Render HTML template
            html_content = self.render_template(template_name, context)
            
            # Create HTML object
            html = HTML(string=html_content, base_url=str(self.templates_dir))
            
            # Prepare CSS
            css_list = []
            if custom_css:
                css_list.append(CSS(string=custom_css, font_config=self.font_config))
            
            # Generate PDF
            pdf_bytes = html.write_pdf(
                stylesheets=css_list if css_list else None,
                font_config=self.font_config
            )
            
            logger.info(f"PDF generated successfully from template '{template_name}' ({len(pdf_bytes)} bytes)")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Failed to generate PDF from template '{template_name}': {str(e)}")
            raise

    def generate_pdf_from_html(
        self,
        html_content: str,
        custom_css: Optional[str] = None
    ) -> bytes:
        """
        Generate PDF directly from HTML string.

        Args:
            html_content: HTML content as string
            custom_css: Optional custom CSS to apply

        Returns:
            PDF file as bytes

        Raises:
            Exception: If PDF generation fails
        """
        try:
            # Create HTML object
            html = HTML(string=html_content)
            
            # Prepare CSS
            css_list = []
            if custom_css:
                css_list.append(CSS(string=custom_css, font_config=self.font_config))
            
            # Generate PDF
            pdf_bytes = html.write_pdf(
                stylesheets=css_list if css_list else None,
                font_config=self.font_config
            )
            
            logger.info(f"PDF generated successfully from HTML string ({len(pdf_bytes)} bytes)")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Failed to generate PDF from HTML string: {str(e)}")
            raise

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

    def preview_template(self, template_name: str, custom_data: Optional[Dict[str, Any]] = None) -> bytes:
        """
        Generate a preview PDF using sample data.

        Args:
            template_name: Name of the template file
            custom_data: Optional custom data to merge with sample data

        Returns:
            PDF bytes for preview
        """
        # Merge sample data with any custom overrides
        preview_data = SAMPLE_RESUME_DATA.copy()
        if custom_data:
            preview_data.update(custom_data)
        
        return self.generate_pdf(template_name, preview_data)

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
