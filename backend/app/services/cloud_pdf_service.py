"""Cloud-based PDF generation service - no local installation required."""

import base64
import logging
from typing import Dict, Any, Optional
from io import BytesIO

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class CloudPdfService:
    """
    Cloud-based PDF generation using free APIs.
    No GTK, WeasyPrint, or local installation required.
    
    Supported providers (in order of preference):
    1. PDFShift - 250 free PDFs/month
    2. HTML2PDF.app - Free tier available
    3. Browserless - Headless Chrome API
    """
    
    def __init__(self):
        self.pdfshift_api_key = getattr(settings, 'PDFSHIFT_API_KEY', None)
        self.html2pdf_api_key = getattr(settings, 'HTML2PDF_API_KEY', None)
        self.browserless_api_key = getattr(settings, 'BROWSERLESS_API_KEY', None)
        
        # Determine available provider
        self.provider = self._detect_provider()
        logger.info(f"Cloud PDF service initialized with provider: {self.provider}")
    
    def _detect_provider(self) -> str:
        """Detect which cloud PDF provider is configured."""
        if self.pdfshift_api_key:
            return "pdfshift"
        elif self.html2pdf_api_key:
            return "html2pdf"
        elif self.browserless_api_key:
            return "browserless"
        else:
            return "none"
    
    def is_available(self) -> bool:
        """Check if any cloud PDF provider is configured."""
        return self.provider != "none"
    
    def get_status(self) -> Dict[str, Any]:
        """Get cloud PDF service status."""
        return {
            "available": self.is_available(),
            "provider": self.provider,
            "providers": {
                "pdfshift": {
                    "configured": bool(self.pdfshift_api_key),
                    "free_tier": "250 PDFs/month",
                    "signup_url": "https://pdfshift.io/"
                },
                "html2pdf": {
                    "configured": bool(self.html2pdf_api_key),
                    "free_tier": "100 PDFs/month",
                    "signup_url": "https://html2pdf.app/"
                },
                "browserless": {
                    "configured": bool(self.browserless_api_key),
                    "free_tier": "1000 API calls/month",
                    "signup_url": "https://browserless.io/"
                }
            },
            "message": self._get_status_message()
        }
    
    def _get_status_message(self) -> str:
        if self.is_available():
            return f"Cloud PDF generation ready using {self.provider}"
        return (
            "No cloud PDF provider configured. Add one of these API keys to .env:\n"
            "  PDFSHIFT_API_KEY - Get free key at https://pdfshift.io/\n"
            "  HTML2PDF_API_KEY - Get free key at https://html2pdf.app/\n"
            "  BROWSERLESS_API_KEY - Get free key at https://browserless.io/"
        )
    
    async def generate_pdf_from_html(
        self,
        html_content: str,
        options: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        Generate PDF from HTML content using cloud provider.
        
        Args:
            html_content: Full HTML document as string
            options: Optional PDF generation options (margins, format, etc.)
            
        Returns:
            PDF file as bytes
            
        Raises:
            RuntimeError: If no provider is configured or generation fails
        """
        if not self.is_available():
            raise RuntimeError(
                "No cloud PDF provider configured. "
                "Get a free API key from pdfshift.io, html2pdf.app, or browserless.io"
            )
        
        options = options or {}
        
        if self.provider == "pdfshift":
            return await self._generate_with_pdfshift(html_content, options)
        elif self.provider == "html2pdf":
            return await self._generate_with_html2pdf(html_content, options)
        elif self.provider == "browserless":
            return await self._generate_with_browserless(html_content, options)
        else:
            raise RuntimeError(f"Unknown provider: {self.provider}")
    
    async def _generate_with_pdfshift(
        self,
        html_content: str,
        options: Dict[str, Any]
    ) -> bytes:
        """Generate PDF using PDFShift API."""
        url = "https://api.pdfshift.io/v3/convert/pdf"
        
        payload = {
            "source": html_content,
            "landscape": options.get("landscape", False),
            "use_print": options.get("use_print", False),
            "format": options.get("format", "Letter"),
        }
        
        # Add margin if specified
        if "margin" in options:
            payload["margin"] = options["margin"]
        
        # Add optional settings
        if "filename" in options:
            payload["filename"] = options["filename"]
        
        # Use X-API-Key header as per PDFShift documentation
        headers = {
            "X-API-Key": self.pdfshift_api_key,
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                url,
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                logger.info(f"PDFShift: PDF generated successfully ({len(response.content)} bytes)")
                return response.content
            else:
                error_msg = f"PDFShift API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
    
    async def _generate_with_html2pdf(
        self,
        html_content: str,
        options: Dict[str, Any]
    ) -> bytes:
        """Generate PDF using HTML2PDF.app API."""
        url = "https://api.html2pdf.app/v1/generate"
        
        payload = {
            "html": html_content,
            "apiKey": self.html2pdf_api_key,
            "format": options.get("format", "Letter"),
            "marginTop": options.get("margin_top", "10mm"),
            "marginBottom": options.get("margin_bottom", "10mm"),
            "marginLeft": options.get("margin_left", "10mm"),
            "marginRight": options.get("margin_right", "10mm"),
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload)
            
            if response.status_code == 200:
                logger.info(f"HTML2PDF: PDF generated successfully ({len(response.content)} bytes)")
                return response.content
            else:
                error_msg = f"HTML2PDF API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
    
    async def _generate_with_browserless(
        self,
        html_content: str,
        options: Dict[str, Any]
    ) -> bytes:
        """Generate PDF using Browserless.io Chrome API."""
        url = f"https://chrome.browserless.io/pdf?token={self.browserless_api_key}"
        
        # Browserless expects the HTML to be base64 encoded or served from URL
        # We'll use the html option with gotoOptions
        payload = {
            "html": html_content,
            "options": {
                "format": options.get("format", "Letter"),
                "printBackground": True,
                "margin": {
                    "top": options.get("margin_top", "10mm"),
                    "bottom": options.get("margin_bottom", "10mm"),
                    "left": options.get("margin_left", "10mm"),
                    "right": options.get("margin_right", "10mm"),
                }
            }
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                logger.info(f"Browserless: PDF generated successfully ({len(response.content)} bytes)")
                return response.content
            else:
                error_msg = f"Browserless API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)


# Global instance
cloud_pdf_service = CloudPdfService()
