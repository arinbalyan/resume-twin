"""LaTeX compilation and rendering service."""

import subprocess
import tempfile
import os
import shutil
from typing import Dict, Any, Optional, List
from pathlib import Path
from uuid import UUID
import logging
from jinja2 import Template, Environment, FileSystemLoader
import re
import base64

from app.core.config import settings
from app.utils.logger import setup_logger
from app.services.s3_service import s3_service

logger = setup_logger(__name__)


class LaTeXService:
    """Service for LaTeX template compilation and rendering."""
    
    def __init__(self):
        """Initialize LaTeX service."""
        self.temp_dir = tempfile.mkdtemp(prefix="resume_twin_")
        self.templates_dir = os.path.join(settings.TEMPLATES_DIR or "templates", "latex")
        
        # Create directories if they don't exist
        os.makedirs(self.templates_dir, exist_ok=True)
        os.makedirs(os.path.join(self.templates_dir, "output"), exist_ok=True)
        
        logger.info(f"LaTeX service initialized with temp dir: {self.temp_dir}")
    
    def __del__(self):
        """Clean up temporary directory."""
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except Exception as e:
                logger.warning(f"Failed to cleanup temp directory: {e}")
    
    def render_template(self, template_content: str, data: Dict[str, Any]) -> str:
        """Render LaTeX template with Jinja2 using user data."""
        try:
            # Create Jinja2 template
            latex_template = Template(template_content)
            
            # Render template with data
            rendered_content = latex_template.render(**data)
            
            # Clean up LaTeX-specific Jinja2 artifacts
            rendered_content = self._cleanup_jinja_artifacts(rendered_content)
            
            return rendered_content
            
        except Exception as e:
            logger.error(f"Error rendering LaTeX template: {e}")
            raise
    
    def _cleanup_jinja_artifacts(self, content: str) -> str:
        """Clean up Jinja2 artifacts that may interfere with LaTeX."""
        # Remove Jinja2 block markers that might cause issues
        content = re.sub(r'{%[^%]*%}', '', content)
        
        # Clean up extra whitespace
        content = re.sub(r'\n\s*\n', '\n\n', content)
        
        return content
    
    def compile_latex(self, latex_content: str, output_name: str = "resume") -> Optional[bytes]:
        """Compile LaTeX content to PDF."""
        try:
            # Check if pdflatex is available
            if not self._check_latex_installation():
                logger.error("pdflatex is not installed or not in PATH")
                raise Exception("LaTeX compiler not found. Please install TeX Live or MiKTeX.")
            
            # Create temporary directory for compilation
            with tempfile.TemporaryDirectory() as temp_dir:
                tex_file = os.path.join(temp_dir, f"{output_name}.tex")
                output_dir = temp_dir
                
                # Write LaTeX file
                with open(tex_file, 'w', encoding='utf-8') as f:
                    f.write(latex_content)
                
                logger.info(f"Compiling LaTeX file: {tex_file}")
                
                # Compile with pdflatex (multiple passes for cross-references)
                for pass_num in range(2):  # Two passes usually sufficient
                    result = subprocess.run(
                        [
                            'pdflatex',
                            '-interaction=nonstopmode',
                            '-halt-on-error',
                            '-output-directory', output_dir,
                            tex_file
                        ],
                        capture_output=True,
                        text=True,
                        timeout=60,  # 60 second timeout
                        cwd=temp_dir
                    )
                    
                    if result.returncode != 0:
                        logger.error(f"LaTeX compilation pass {pass_num + 1} failed:")
                        logger.error(f"STDOUT: {result.stdout}")
                        logger.error(f"STDERR: {result.stderr}")
                        if pass_num == 0:  # Fail immediately on first pass
                            raise Exception(f"LaTeX compilation failed: {result.stderr[:500]}")
                        break
                    
                    logger.info(f"Compilation pass {pass_num + 1} completed successfully")
                    
                    # Check if we need another pass
                    if pass_num > 0 and 'Rerun' not in result.stdout:
                        break  # Compilation successful
                
                # Read PDF file
                pdf_file = os.path.join(output_dir, f"{output_name}.pdf")
                if os.path.exists(pdf_file):
                    with open(pdf_file, 'rb') as f:
                        pdf_bytes = f.read()
                        logger.info(f"PDF generated successfully: {len(pdf_bytes)} bytes")
                        return pdf_bytes
                else:
                    # Try to find any PDF file created
                    pdf_files = list(Path(output_dir).glob("*.pdf"))
                    if pdf_files:
                        with open(pdf_files[0], 'rb') as f:
                            return f.read()
                    else:
                        raise Exception("No PDF file was generated")
                        
        except subprocess.TimeoutExpired:
            logger.error("LaTeX compilation timed out")
            raise Exception("LaTeX compilation timed out after 60 seconds")
        except Exception as e:
            logger.error(f"Error compiling LaTeX: {e}")
            raise
    
    def _check_latex_installation(self) -> bool:
        """Check if LaTeX is installed and available."""
        try:
            result = subprocess.run(
                ['pdflatex', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def check_latex_installation(self) -> bool:
        """Public method to check if LaTeX is installed and available."""
        return self._check_latex_installation()
    
    def compile_with_fallback(self, latex_content: str, output_name: str = "resume") -> Optional[bytes]:
        """Try LaTeX compilation with fallback methods."""
        try:
            # First attempt: Standard LaTeX compilation
            return self.compile_latex(latex_content, output_name)
            
        except Exception as e:
            logger.warning(f"Primary LaTeX compilation failed: {e}")
            
            try:
                # Fallback 1: Try with different engine (if available)
                return self._compile_with_xelatex(latex_content, output_name)
            except:
                logger.warning("XeLaTeX compilation also failed")
                
            try:
                # Fallback 2: HTML to PDF conversion (if we have HTML version)
                return self._compile_html_fallback(latex_content, output_name)
            except:
                logger.error("All LaTeX compilation methods failed")
                raise
    
    def _compile_with_xelatex(self, latex_content: str, output_name: str) -> Optional[bytes]:
        """Try compilation with XeLaTeX."""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                tex_file = os.path.join(temp_dir, f"{output_name}.tex")
                
                # Write LaTeX file
                with open(tex_file, 'w', encoding='utf-8') as f:
                    f.write(latex_content)
                
                # Try XeLaTeX
                result = subprocess.run(
                    ['xelatex', '-interaction=nonstopmode', tex_file],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=temp_dir
                )
                
                if result.returncode == 0:
                    pdf_file = os.path.join(temp_dir, f"{output_name}.pdf")
                    if os.path.exists(pdf_file):
                        with open(pdf_file, 'rb') as f:
                            return f.read()
                
                raise Exception(f"XeLaTeX compilation failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"XeLaTeX compilation error: {e}")
            raise
    
    def _compile_html_fallback(self, latex_content: str, output_name: str) -> Optional[bytes]:
        """Fallback HTML to PDF conversion."""
        try:
            # Convert LaTeX to HTML (basic conversion)
            html_content = self._latex_to_html(latex_content)
            
            # This would require additional libraries like weasyprint or wkhtmltopdf
            # For now, raise an exception as this is a complex fallback
            raise Exception("HTML to PDF fallback not implemented")
            
        except Exception as e:
            logger.error(f"HTML fallback compilation error: {e}")
            raise
    
    def _latex_to_html(self, latex_content: str) -> str:
        """Basic LaTeX to HTML conversion."""
        # This is a very basic conversion - in production, you'd use a proper converter
        html_content = latex_content
        html_content = re.sub(r'\\begin\{document\}', '<html><body>', html_content)
        html_content = re.sub(r'\\end\{document\}', '</body></html>', html_content)
        html_content = re.sub(r'\\section\{([^}]*)\}', r'<h1>\1</h1>', html_content)
        html_content = re.sub(r'\\subsection\{([^}]*)\}', r'<h2>\1</h2>', html_content)
        return html_content
    
    def generate_preview_image(self, latex_content: str, output_name: str = "preview") -> Optional[bytes]:
        """Generate preview image from LaTeX (requires additional tools)."""
        try:
            # This would require pdftoppm or similar tools
            # For now, return None as this is advanced functionality
            logger.warning("Preview image generation not implemented")
            return None
            
        except Exception as e:
            logger.error(f"Error generating preview image: {e}")
            return None
    
    def validate_template(self, template_content: str) -> Dict[str, Any]:
        """Validate LaTeX template syntax."""
        try:
            # Test compilation with minimal data
            test_data = {
                "user_name": "Test User",
                "email": "test@example.com",
                "phone": "123-456-7890"
            }
            
            rendered = self.render_template(template_content, test_data)
            
            # Try compilation
            pdf_content = self.compile_latex(rendered, "validation_test")
            
            return {
                "valid": True,
                "warnings": [],
                "errors": [],
                "compilation_successful": True
            }
            
        except Exception as e:
            return {
                "valid": False,
                "warnings": [],
                "errors": [str(e)],
                "compilation_successful": False
            }
    
    def extract_template_variables(self, template_content: str) -> List[str]:
        """Extract template variables from LaTeX template."""
        try:
            # Find Jinja2 template variables
            variables = set()
            
            # Find {{ variable }} patterns
            simple_vars = re.findall(r'\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}', template_content)
            variables.update(simple_vars)
            
            # Find {% for variable in list %} patterns
            for_vars = re.findall(r'\{\%\s*for\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+in', template_content)
            variables.update(for_vars)
            
            # Find {% if variable %} patterns
            if_vars = re.findall(r'\{\%\s*if\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\%\}', template_content)
            variables.update(if_vars)
            
            return sorted(list(variables))
            
        except Exception as e:
            logger.error(f"Error extracting template variables: {e}")
            return []
    
    def template_compatibility_check(self, template_content: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check template compatibility with user data."""
        try:
            required_vars = self.extract_template_variables(template_content)
            missing_vars = []
            available_vars = []
            
            for var in required_vars:
                if var in user_data:
                    available_vars.append(var)
                else:
                    missing_vars.append(var)
            
            return {
                "compatible": len(missing_vars) == 0,
                "required_variables": required_vars,
                "available_variables": available_vars,
                "missing_variables": missing_vars,
                "compatibility_score": len(available_vars) / len(required_vars) if required_vars else 1.0
            }
            
        except Exception as e:
            logger.error(f"Error checking template compatibility: {e}")
            return {
                "compatible": False,
                "required_variables": [],
                "available_variables": [],
                "missing_variables": [],
                "compatibility_score": 0.0
            }


# Global LaTeX service instance
latex_service = LaTeXService()


def compile_resume(
    template_content: str,
    user_data: Dict[str, Any],
    output_name: str = "resume"
) -> Dict[str, Any]:
    """Complete resume compilation workflow."""
    try:
        logger.info("Starting resume compilation")
        
        # Render template
        rendered_latex = latex_service.render_template(template_content, user_data)
        
        # Compile to PDF
        pdf_content = latex_service.compile_with_fallback(rendered_latex, output_name)
        
        # Generate filename
        pdf_filename = f"{output_name}.pdf"
        
        return {
            "success": True,
            "pdf_content": pdf_content,
            "filename": pdf_filename,
            "size": len(pdf_content),
            "template_rendering_successful": True,
            "compilation_successful": True
        }
        
    except Exception as e:
        logger.error(f"Resume compilation failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "template_rendering_successful": False,
            "compilation_successful": False
        }