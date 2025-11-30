"""PDF generation factory service that selects the appropriate generation method."""

import logging
from typing import Dict, Any, Optional
from enum import Enum

from app.core.config import settings
from app.services.latex_service import latex_service
from app.services.html_to_pdf_service import html_to_pdf_service
from app.services.overleaf_service import overleaf_service

logger = logging.getLogger(__name__)


class PdfGenerationMethod(str, Enum):
    """Supported PDF generation methods."""
    LATEX = "latex"
    HTML = "html"
    OVERLEAF = "overleaf"


class PdfGeneratorFactory:
    """Factory for selecting and using the appropriate PDF generation method."""

    def __init__(self):
        """Initialize the PDF generator factory."""
        self.method = PdfGenerationMethod(settings.PDF_GENERATION_METHOD.lower())
        logger.info(f"PDF Generator Factory initialized with method: {self.method.value}")

    def generate_resume_pdf(
        self,
        template_name: str,
        context: Dict[str, Any],
        method: Optional[PdfGenerationMethod] = None
    ) -> bytes:
        """
        Generate PDF resume using the configured or specified method.

        Args:
            template_name: Name of the template (without extension)
            context: Template context data
            method: Override the configured method (optional)

        Returns:
            PDF file as bytes

        Raises:
            ValueError: If method is not supported or not available
            Exception: If PDF generation fails
        """
        # Use specified method or default
        generation_method = method or self.method
        
        logger.info(f"Generating resume PDF using method: {generation_method.value}")
        
        try:
            if generation_method == PdfGenerationMethod.LATEX:
                return self._generate_with_latex(template_name, context)
            elif generation_method == PdfGenerationMethod.HTML:
                return self._generate_with_html(template_name, context)
            elif generation_method == PdfGenerationMethod.OVERLEAF:
                return self._generate_with_overleaf(template_name, context)
            else:
                raise ValueError(f"Unsupported PDF generation method: {generation_method}")
                
        except Exception as e:
            logger.error(f"PDF generation failed with method '{generation_method.value}': {str(e)}")
            
            # Try fallback if primary method fails
            if generation_method != PdfGenerationMethod.HTML:
                logger.info("Attempting fallback to HTML-to-PDF method")
                try:
                    return self._generate_with_html(template_name, context)
                except Exception as fallback_error:
                    logger.error(f"Fallback also failed: {str(fallback_error)}")
            
            raise

    def _generate_with_latex(self, template_name: str, context: Dict[str, Any]) -> bytes:
        """
        Generate PDF using local LaTeX compilation.

        Args:
            template_name: Template name (will append .tex)
            context: Template context

        Returns:
            PDF bytes

        Raises:
            Exception: If LaTeX compilation fails
        """
        logger.info(f"Generating PDF with local LaTeX: {template_name}")
        
        # Add .tex extension if not present
        if not template_name.endswith('.tex'):
            template_name = f"{template_name}.tex"
        
        # Render LaTeX template
        latex_content = latex_service.render_template(template_name, context)
        
        # Compile to PDF
        pdf_bytes = latex_service.compile_latex(latex_content)
        
        return pdf_bytes

    def _generate_with_html(self, template_name: str, context: Dict[str, Any]) -> bytes:
        """
        Generate PDF using HTML-to-PDF conversion.

        Args:
            template_name: Template name (will append .html)
            context: Template context

        Returns:
            PDF bytes

        Raises:
            Exception: If HTML-to-PDF conversion fails
        """
        logger.info(f"Generating PDF with HTML-to-PDF: {template_name}")
        
        # Add .html extension if not present
        if not template_name.endswith('.html'):
            template_name = f"{template_name}.html"
        
        # Generate PDF from HTML template
        pdf_bytes = html_to_pdf_service.generate_pdf(template_name, context)
        
        return pdf_bytes

    async def _generate_with_overleaf(self, template_name: str, context: Dict[str, Any]) -> bytes:
        """
        Generate PDF using Overleaf API.

        Args:
            template_name: Template name (will append .tex)
            context: Template context

        Returns:
            PDF bytes

        Raises:
            ValueError: If Overleaf API not configured
            Exception: If Overleaf compilation fails
        """
        logger.info(f"Generating PDF with Overleaf API: {template_name}")
        
        if not overleaf_service.is_available():
            raise ValueError("Overleaf API is not configured. Please set OVERLEAF_API_URL and OVERLEAF_API_TOKEN")
        
        # Add .tex extension if not present
        if not template_name.endswith('.tex'):
            template_name = f"{template_name}.tex"
        
        # Render LaTeX template
        latex_content = latex_service.render_template(template_name, context)
        
        # Compile using Overleaf API
        pdf_bytes = await overleaf_service.compile_latex(
            latex_content,
            project_name=context.get('user_name', 'Resume')
        )
        
        return pdf_bytes

    def get_available_templates(self, method: Optional[PdfGenerationMethod] = None) -> list[str]:
        """
        Get list of available templates for the specified method.

        Args:
            method: Generation method (uses default if not specified)

        Returns:
            List of template names
        """
        generation_method = method or self.method
        
        if generation_method == PdfGenerationMethod.HTML:
            templates = html_to_pdf_service.list_available_templates()
            # Remove extensions for consistent naming
            return [t.replace('.html', '') for t in templates]
        else:
            # For LaTeX and Overleaf, use LaTeX templates
            templates = latex_service.list_available_templates()
            # Remove extensions for consistent naming
            return [t.replace('.tex', '') for t in templates]

    def get_method_status(self) -> Dict[str, Any]:
        """
        Get status of all PDF generation methods.

        Returns:
            Dictionary with method availability status
        """
        status = {
            "configured_method": self.method.value,
            "methods": {
                "latex": {
                    "available": latex_service.check_latex_installation(),
                    "description": "Local LaTeX compilation (pdflatex)"
                },
                "html": {
                    "available": settings.HTML_TO_PDF_ENABLED,
                    "description": "HTML-to-PDF conversion (WeasyPrint)"
                },
                "overleaf": {
                    "available": overleaf_service.is_available(),
                    "description": "Overleaf API cloud compilation"
                }
            }
        }
        
        return status


# Global instance
pdf_generator = PdfGeneratorFactory()
