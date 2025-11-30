# Multi-Method PDF Generation System

## Quick Start

### 1. Choose Your PDF Generation Method

Set in `.env`:

```bash
# Fast & lightweight (Recommended for most cases)
PDF_GENERATION_METHOD=html

# Or use LaTeX for professional typesetting
# PDF_GENERATION_METHOD=latex

# Or use Overleaf API for cloud-based LaTeX
# PDF_GENERATION_METHOD=overleaf
```

### 2. Install Dependencies

```bash
# For HTML method (lightweight)
pip install weasyprint

# For LaTeX method (requires system packages)
# Windows: Install MiKTeX from https://miktex.org
# macOS: brew install --cask mactex
# Linux: sudo apt-get install texlive-full

# For Overleaf method (requires API key)
# Get API key from https://www.overleaf.com/user/settings
```

### 3. Start the Server

```bash
cd backend
uvicorn app.main:app --reload
```

### 4. Generate a Resume

```bash
curl -X POST http://localhost:8000/api/v1/resume/generate \
  -H "Content-Type: application/json" \
  -d '{
    "template_name": "professional_resume",
    "title": "My Software Engineer Resume",
    "selected_tags": ["web-dev", "backend"]
  }'
```

## Templates

### HTML Templates (Fast)
Located in `templates/html/`:
- `professional_resume.html` - Modern professional design
- Easy to customize with CSS
- No LaTeX knowledge required

### LaTeX Templates (Professional)
Located in `templates/latex/`:
- `professional_resume.tex` - Professional LaTeX design
- Best typography quality
- Requires LaTeX knowledge

## Switching Methods

You can switch between methods without changing any code:

```bash
# In .env file
PDF_GENERATION_METHOD=html   # Fast, no LaTeX needed
# OR
PDF_GENERATION_METHOD=latex  # High quality, requires LaTeX
# OR
PDF_GENERATION_METHOD=overleaf  # Cloud LaTeX, needs API key
```

Restart the server and the new method will be used automatically!

## API Endpoints

### Generate Resume
```http
POST /api/v1/resume/generate
```

### Check Method Status
```http
GET /api/v1/resume/generation-methods/status
```

Returns:
```json
{
  "configured_method": "html",
  "methods": {
    "latex": {"available": false, "description": "..."},
    "html": {"available": true, "description": "..."},
    "overleaf": {"available": false, "description": "..."}
  }
}
```

### List Available Templates
```http
GET /api/v1/resume/templates/list
```

## Docker Deployment

### HTML Method (Lightweight - 200MB)
```dockerfile
FROM python:3.13-slim
# WeasyPrint dependencies only
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 fonts-liberation
```

### LaTeX Method (Full - 700MB)
```dockerfile
FROM python:3.13-slim
# Full LaTeX installation
RUN apt-get update && apt-get install -y \
    texlive-latex-base texlive-latex-extra \
    texlive-fonts-recommended texlive-fonts-extra
```

## Environment Variables

```bash
# PDF Generation Method
PDF_GENERATION_METHOD=html  # html | latex | overleaf

# HTML-to-PDF Settings
HTML_TO_PDF_ENABLED=true

# LaTeX Settings
LATEX_COMPILATION_TIMEOUT=60

# Overleaf API Settings (optional)
OVERLEAF_API_URL=https://api.overleaf.com/v1
OVERLEAF_API_TOKEN=your-token
OVERLEAF_TEMPLATE_ID=your-template-id
```

## Troubleshooting

### HTML Method
**Problem**: Fonts not loading
```bash
# Install additional fonts
sudo apt-get install fonts-noto fonts-dejavu
```

### LaTeX Method
**Problem**: `pdflatex: command not found`
```bash
# Install LaTeX
sudo apt-get install texlive-latex-base texlive-latex-extra
```

### Overleaf Method
**Problem**: API authentication failed
- Check `OVERLEAF_API_TOKEN` is correct
- Verify API subscription is active

## Performance

| Method | Speed | Quality | Docker Size | Best For |
|--------|-------|---------|-------------|----------|
| HTML | ⚡ 500ms | ⭐⭐⭐⭐ | 200MB | Production |
| LaTeX | 🐌 3s | ⭐⭐⭐⭐⭐ | 700MB | Academic |
| Overleaf | ⚡ 2s | ⭐⭐⭐⭐⭐ | 150MB | Serverless |

## Documentation

For detailed documentation, see:
- [PDF Generation Methods Guide](./pdf-generation-methods-guide.md)
- [LaTeX Deployment Guide](./latex-deployment-guide.md)

## Example Usage

```python
from app.services.pdf_generator_factory import pdf_generator

# Generate PDF (method selected automatically from .env)
pdf_bytes = pdf_generator.generate_resume_pdf(
    template_name="professional_resume",
    context={
        "user_name": "John Doe",
        "email": "john@example.com",
        "summary": "Experienced software engineer...",
        "projects": [...],
        "experience": [...],
        "education": [...]
    }
)
```

## Contributing

When adding new templates:

1. Create both HTML and LaTeX versions:
   - `templates/html/my_template.html`
   - `templates/latex/my_template.tex`

2. Test with all methods:
   ```bash
   PDF_GENERATION_METHOD=html pytest tests/
   PDF_GENERATION_METHOD=latex pytest tests/
   ```

3. Update template list in documentation

## Support

For issues or questions:
- Check the [troubleshooting guide](./pdf-generation-methods-guide.md#troubleshooting)
- Open an issue on GitHub
- Contact: team@resumetwin.com
