# PDF Generation Quick Reference Card

## Environment Variable

```bash
# In .env file - choose ONE:
PDF_GENERATION_METHOD=html      # ⚡ Fast, lightweight (Recommended)
PDF_GENERATION_METHOD=latex     # 🎓 High quality, academic
PDF_GENERATION_METHOD=overleaf  # ☁️  Cloud-based LaTeX
```

## Method Comparison

| Feature | HTML | LaTeX | Overleaf |
|---------|------|-------|----------|
| Speed | ⚡⚡⚡ 500ms | 🐌 3s | ⚡⚡ 2s |
| Quality | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Setup | ✅ Easy | ⚠️ Complex | ✅ Easy |
| Docker Size | 200MB | 700MB | 150MB |
| Requirements | pip install | TeX Live | API Key |
| Best For | Production | Academic | Serverless |

## Quick Setup

### HTML (Recommended)
```bash
# .env
PDF_GENERATION_METHOD=html
HTML_TO_PDF_ENABLED=true

# Install
pip install weasyprint

# Docker: Automatic (included in Dockerfile)
```

### LaTeX
```bash
# .env
PDF_GENERATION_METHOD=latex
LATEX_COMPILATION_TIMEOUT=60

# Install
# Windows: Download MiKTeX from https://miktex.org
# macOS: brew install --cask mactex
# Linux: sudo apt-get install texlive-full

# Docker: Automatic (included in Dockerfile)
```

### Overleaf
```bash
# .env
PDF_GENERATION_METHOD=overleaf
OVERLEAF_API_URL=https://api.overleaf.com/v1
OVERLEAF_API_TOKEN=your-token-here
OVERLEAF_TEMPLATE_ID=optional-template-id

# No local installation needed!
```

## API Endpoints

### Generate Resume
```http
POST /api/v1/resume/generate
Content-Type: application/json

{
  "template_name": "professional_resume",
  "title": "Software Engineer Resume",
  "selected_tags": ["web-dev", "backend"]
}
```

### Check Status
```http
GET /api/v1/resume/generation-methods/status

Response:
{
  "configured_method": "html",
  "methods": {
    "latex": {"available": false},
    "html": {"available": true},
    "overleaf": {"available": false}
  }
}
```

## Troubleshooting

### "pdflatex: command not found"
```bash
# LaTeX not installed
# Solution: Install TeX Live or switch to HTML method
PDF_GENERATION_METHOD=html
```

### "Overleaf API authentication failed"
```bash
# Invalid API token
# Solution: Check OVERLEAF_API_TOKEN in .env
```

### "Font rendering issues"
```bash
# Missing fonts for WeasyPrint
# Solution:
sudo apt-get install fonts-liberation fonts-noto
```

## Templates

### Directory Structure
```
templates/
├── html/
│   └── professional_resume.html  ← HTML method uses this
└── latex/
    └── professional_resume.tex   ← LaTeX/Overleaf use this
```

### Template Naming
```python
# API request (no extension)
{"template_name": "professional_resume"}

# System automatically selects:
# - professional_resume.html (if method=html)
# - professional_resume.tex (if method=latex/overleaf)
```

## Docker Commands

### Build
```bash
# Includes all methods
docker build -t resume-twin-backend .
```

### Run with HTML
```bash
docker run -p 8000:8000 \
  -e PDF_GENERATION_METHOD=html \
  resume-twin-backend
```

### Run with LaTeX
```bash
docker run -p 8000:8000 \
  -e PDF_GENERATION_METHOD=latex \
  resume-twin-backend
```

## Performance Tips

### For Production
```bash
PDF_GENERATION_METHOD=html  # Fastest, cheapest
```

### For Best Quality
```bash
PDF_GENERATION_METHOD=latex  # Best typography
```

### For Serverless
```bash
PDF_GENERATION_METHOD=overleaf  # Smallest package
# OR
PDF_GENERATION_METHOD=html  # No external API
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Slow generation | Switch to HTML method |
| Poor typography | Switch to LaTeX method |
| Large Docker image | Use HTML method |
| LaTeX errors | Check template syntax or use HTML |
| API limits | Use local method (HTML/LaTeX) |
| Missing fonts | Install fonts-liberation package |

## Dependencies

### HTML Method
```txt
weasyprint>=60.1
libpango-1.0-0
libpangocairo-1.0-0
fonts-liberation
```

### LaTeX Method
```txt
texlive-latex-base
texlive-latex-extra
texlive-fonts-recommended
texlive-xetex
```

### Overleaf Method
```txt
httpx>=0.25.2
(No system dependencies!)
```

## Code Example

```python
from app.services.pdf_generator_factory import pdf_generator

# Generate PDF (method auto-selected from .env)
pdf_bytes = pdf_generator.generate_resume_pdf(
    template_name="professional_resume",
    context={
        "user_name": "John Doe",
        "email": "john@example.com",
        "projects": [...],
        # ... more data
    }
)

# Check what methods are available
status = pdf_generator.get_method_status()
print(status["configured_method"])  # "html"
```

## Environment Variables Cheat Sheet

```bash
# Required for all methods
PDF_GENERATION_METHOD=html|latex|overleaf
TEMPLATES_DIR=templates

# HTML-specific
HTML_TO_PDF_ENABLED=true

# LaTeX-specific
LATEX_COMPILATION_TIMEOUT=60

# Overleaf-specific
OVERLEAF_API_URL=https://api.overleaf.com/v1
OVERLEAF_API_TOKEN=your-token
OVERLEAF_TEMPLATE_ID=optional-id
```

## Testing Locally

```bash
# 1. Set method in .env
echo "PDF_GENERATION_METHOD=html" >> .env

# 2. Start server
uvicorn app.main:app --reload

# 3. Test generation
curl -X POST http://localhost:8000/api/v1/resume/generate \
  -H "Content-Type: application/json" \
  -d '{"template_name": "professional_resume", "title": "Test"}'

# 4. Check status
curl http://localhost:8000/api/v1/resume/generation-methods/status
```

## Migration from LaTeX-Only

```bash
# Step 1: Add to .env
PDF_GENERATION_METHOD=html
HTML_TO_PDF_ENABLED=true

# Step 2: Install dependency
pip install weasyprint

# Step 3: Restart server
# Done! No code changes needed
```

## When to Use Each Method

### Use HTML When:
- ✅ Deploying to Render/Heroku/Railway
- ✅ Need fast response times
- ✅ Want smaller Docker images
- ✅ Modern web-based designs

### Use LaTeX When:
- ✅ Academic/research resumes
- ✅ Self-hosted environment
- ✅ Need perfect typography
- ✅ Mathematical notation required

### Use Overleaf When:
- ✅ Deploying to AWS Lambda
- ✅ Want LaTeX quality without installation
- ✅ Have Overleaf API subscription
- ✅ Serverless architecture

---

**📚 Full Documentation**: See `docs/pdf-generation-methods-guide.md`

**🚀 Quick Start**: See `docs/PDF_GENERATION_README.md`

**❓ Issues**: Check troubleshooting section in main guide
