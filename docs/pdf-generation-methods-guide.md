# PDF Generation Methods Configuration Guide

## Overview

The Resume Twin backend now supports **three different PDF generation methods**, configurable via environment variables. This allows you to choose the best method based on your deployment environment, performance needs, and resource availability.

## Available Methods

### 1. **HTML-to-PDF (Recommended)** 
- **Method**: `PDF_GENERATION_METHOD=html`
- **Technology**: WeasyPrint
- **Pros**:
  - ✅ No LaTeX installation required
  - ✅ Faster generation (~500ms per resume)
  - ✅ Smaller Docker image (~200MB vs ~700MB with LaTeX)
  - ✅ Easier deployment (fewer dependencies)
  - ✅ Better HTML/CSS support for modern designs
  - ✅ Works on all platforms (Windows, macOS, Linux)
- **Cons**:
  - ❌ Less precise typography than LaTeX
  - ❌ Limited mathematical notation support
- **Best For**: Modern web-based designs, quick deployments, serverless environments

### 2. **Local LaTeX Compilation**
- **Method**: `PDF_GENERATION_METHOD=latex`
- **Technology**: pdflatex/xelatex
- **Pros**:
  - ✅ Professional typesetting quality
  - ✅ Perfect for academic/research resumes
  - ✅ Full LaTeX package ecosystem
  - ✅ Mathematical notation support
- **Cons**:
  - ❌ Requires full texlive installation (~500MB)
  - ❌ Slower compilation (2-5 seconds per resume)
  - ❌ Complex setup on some platforms
  - ❌ Higher resource usage
- **Best For**: Academic resumes, precise typography requirements, on-premise deployments

### 3. **Overleaf API (Cloud-based LaTeX)**
- **Method**: `PDF_GENERATION_METHOD=overleaf`
- **Technology**: Overleaf Cloud API
- **Pros**:
  - ✅ No local LaTeX installation needed
  - ✅ Professional LaTeX quality
  - ✅ Offloads compilation to cloud
  - ✅ Smaller Docker image
- **Cons**:
  - ❌ Requires Overleaf API subscription
  - ❌ Network dependency
  - ❌ API rate limits
  - ❌ Additional cost
- **Best For**: Serverless deployments, when LaTeX quality is required but local installation isn't feasible

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# ========================================
# PDF GENERATION CONFIGURATION
# ========================================

# Choose your method: "html", "latex", or "overleaf"
PDF_GENERATION_METHOD=html

# --- HTML-to-PDF Settings ---
HTML_TO_PDF_ENABLED=true

# --- LaTeX Settings ---
LATEX_COMPILATION_TIMEOUT=60
# Optional: External compilation service
# LATEX_COMPILE_SERVER_URL=https://your-latex-service.com

# --- Overleaf API Settings ---
# OVERLEAF_API_URL=https://api.overleaf.com/v1
# OVERLEAF_API_TOKEN=your-token-here
# OVERLEAF_TEMPLATE_ID=your-template-id

# --- Common Settings ---
TEMPLATES_DIR=templates
```

## Template Structure

Templates for each method are stored in separate directories:

```
templates/
├── html/
│   ├── professional_resume.html
│   ├── modern_resume.html
│   └── minimal_resume.html
└── latex/
    ├── professional_resume.tex
    ├── academic_resume.tex
    └── modern_resume.tex
```

### Template Naming Convention

When calling the API, use the template name **without extension**:
- `template_name: "professional_resume"` → Will use `professional_resume.html` or `professional_resume.tex` based on `PDF_GENERATION_METHOD`

## API Usage

### Generate Resume

```bash
POST /api/v1/resume/generate
Content-Type: application/json

{
  "template_name": "professional_resume",
  "title": "Software Engineer Resume",
  "selected_tags": ["web-dev", "backend"],
  "customizations": {
    "color_scheme": "yellow-navy"
  }
}
```

### Check Available Methods

```bash
GET /api/v1/resume/generation-methods/status
```

Response:
```json
{
  "configured_method": "html",
  "methods": {
    "latex": {
      "available": true,
      "description": "Local LaTeX compilation (pdflatex)"
    },
    "html": {
      "available": true,
      "description": "HTML-to-PDF conversion (WeasyPrint)"
    },
    "overleaf": {
      "available": false,
      "description": "Overleaf API cloud compilation"
    }
  }
}
```

### List Templates

```bash
GET /api/v1/resume/templates/list
```

Response:
```json
{
  "templates": [
    {
      "name": "professional_resume",
      "filename": "professional_resume.html",
      "method": "html"
    }
  ],
  "generation_method": {
    "configured_method": "html",
    "methods": { ... }
  }
}
```

## Docker Deployment

### HTML-to-PDF (Lightweight)

```dockerfile
FROM python:3.13-slim

# Install WeasyPrint dependencies
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# ... rest of Dockerfile
```

**Image Size**: ~200MB

### LaTeX (Full)

```dockerfile
FROM python:3.13-slim

# Install LaTeX and WeasyPrint dependencies
RUN apt-get update && apt-get install -y \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-xetex \
    lmodern \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# ... rest of Dockerfile
```

**Image Size**: ~700MB

## Switching Between Methods

### At Runtime (via .env)

Simply change the environment variable and restart:

```bash
# Switch to HTML
PDF_GENERATION_METHOD=html

# Switch to LaTeX
PDF_GENERATION_METHOD=latex

# Switch to Overleaf
PDF_GENERATION_METHOD=overleaf
```

No code changes required!

### Fallback Behavior

The system automatically falls back to HTML-to-PDF if the primary method fails:

```python
try:
    pdf = generate_with_latex(...)
except Exception:
    # Automatic fallback to HTML
    pdf = generate_with_html(...)
```

## Performance Comparison

| Method | Avg Time | CPU Usage | Memory | Docker Size |
|--------|----------|-----------|---------|-------------|
| HTML   | ~500ms   | Low       | ~100MB  | ~200MB      |
| LaTeX  | ~3s      | High      | ~200MB  | ~700MB      |
| Overleaf| ~2s     | Very Low  | ~50MB   | ~150MB      |

## Cloud Deployment Recommendations

### Render.com / Railway / Heroku
**Recommended**: `PDF_GENERATION_METHOD=html`
- Faster builds
- Lower resource usage
- Cheaper pricing tier

### AWS Lambda / Vercel / Netlify Functions
**Recommended**: `PDF_GENERATION_METHOD=overleaf` or `PDF_GENERATION_METHOD=html`
- Serverless-friendly
- No large binaries
- Fast cold starts

### Self-hosted / VPS / Dedicated Server
**Recommended**: `PDF_GENERATION_METHOD=latex`
- Full control
- Best quality
- No external dependencies

### Docker Compose / Kubernetes
**Recommended**: Any method
- All methods well-supported
- Easy to swap via ConfigMap

## Template Migration

### Converting LaTeX to HTML

If you have existing LaTeX templates, create HTML equivalents:

**LaTeX**:
```latex
\textbf{{\large #1}} \hfill \textit{\color{subtext}#2}
```

**HTML**:
```html
<div class="entry-header">
  <span class="entry-title">{{ title }}</span>
  <span class="entry-date">{{ date }}</span>
</div>
```

### Converting HTML to LaTeX

**HTML**:
```html
<div class="tech-tag">{{ technology }}</div>
```

**LaTeX**:
```latex
\colorbox{accent}{\color{primary}\texttt{#1}}
```

## Troubleshooting

### HTML Method Issues

**Problem**: Fonts not rendering correctly
```bash
# Install additional fonts
apt-get install fonts-noto fonts-dejavu
```

**Problem**: CSS not applying
- Check `base_url` parameter in WeasyPrint
- Ensure CSS is embedded in HTML template

### LaTeX Method Issues

**Problem**: `pdflatex: command not found`
```bash
# Install LaTeX
sudo apt-get install texlive-latex-base texlive-latex-extra
```

**Problem**: Compilation timeout
```bash
# Increase timeout in .env
LATEX_COMPILATION_TIMEOUT=120
```

### Overleaf Method Issues

**Problem**: API authentication failed
- Verify `OVERLEAF_API_TOKEN` is correct
- Check API subscription status

**Problem**: Rate limit exceeded
- Implement request queuing
- Consider upgrading Overleaf plan

## Best Practices

### 1. Use HTML for Production
Unless you specifically need LaTeX features, HTML-to-PDF is recommended for:
- Faster response times
- Easier maintenance
- Lower costs
- Better CI/CD

### 2. Keep Both Templates Updated
Maintain both HTML and LaTeX versions of templates for flexibility:
```
templates/
├── html/
│   └── professional_resume.html
└── latex/
    └── professional_resume.tex
```

### 3. Test All Methods Locally
Before deploying, test PDF generation with all methods:

```bash
# Test HTML
PDF_GENERATION_METHOD=html pytest tests/

# Test LaTeX
PDF_GENERATION_METHOD=latex pytest tests/

# Test Overleaf (requires API key)
PDF_GENERATION_METHOD=overleaf pytest tests/
```

### 4. Monitor Performance
Track generation times and failures:

```python
logger.info(f"PDF generated in {duration}s using {method}")
```

### 5. Implement Caching
Cache generated PDFs to avoid regeneration:

```python
cache_key = f"resume:{user_id}:{template}:{hash(data)}"
```

## Security Considerations

### HTML Method
- ✅ Sanitize user input to prevent XSS
- ✅ Limit external resource loading
- ✅ Validate CSS injection

### LaTeX Method
- ✅ Sanitize LaTeX special characters
- ✅ Disable `\write18` (shell escape)
- ✅ Use timeout protection
- ✅ Run in sandboxed container

### Overleaf Method
- ✅ Secure API token storage
- ✅ Validate project cleanup
- ✅ Monitor API usage

## Cost Analysis

### Monthly Costs (1000 resumes/month)

| Method | Compute | Storage | External | Total |
|--------|---------|---------|----------|-------|
| HTML   | $5      | $1      | $0       | **$6** |
| LaTeX  | $15     | $1      | $0       | **$16** |
| Overleaf| $3     | $1      | $10      | **$14** |

*Estimates based on Render.com pricing*

## Migration Guide

### From LaTeX-Only to Multi-Method

1. **Add HTML templates**:
   ```bash
   cp templates/latex/professional_resume.tex \
      templates/html/professional_resume.html
   # Convert LaTeX to HTML
   ```

2. **Update .env**:
   ```bash
   PDF_GENERATION_METHOD=html
   HTML_TO_PDF_ENABLED=true
   ```

3. **Test generation**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/resume/generate \
     -H "Content-Type: application/json" \
     -d '{"template_name": "professional_resume", "title": "Test"}'
   ```

4. **Deploy**:
   ```bash
   docker build -t resume-twin-backend .
   docker run -p 8000:8000 resume-twin-backend
   ```

## Support Matrix

| Platform | HTML | LaTeX | Overleaf |
|----------|------|-------|----------|
| Windows  | ✅   | ⚠️*   | ✅       |
| macOS    | ✅   | ✅    | ✅       |
| Linux    | ✅   | ✅    | ✅       |
| Docker   | ✅   | ✅    | ✅       |
| Lambda   | ✅   | ❌    | ✅       |

*Requires MiKTeX installation

## Conclusion

Choose your PDF generation method based on your needs:

- **Quick deployment?** → Use `html`
- **Best quality?** → Use `latex`
- **Serverless?** → Use `overleaf` or `html`
- **Academic resumes?** → Use `latex`
- **Modern designs?** → Use `html`

The system is designed to be flexible - you can switch methods at any time without code changes!
