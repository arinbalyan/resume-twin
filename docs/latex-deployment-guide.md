# LaTeX Setup for Deployment

This document describes how to setup LaTeX for PDF resume generation in production environments.

## Local Development

### Windows
1. Install MiKTeX: https://miktex.org/download
2. Add to PATH: `C:\Program Files\MiKTeX\miktex\bin\x64\`
3. Install required packages:
   ```powershell
   miktex packages install lato fontawesome5 titlesec
   ```

### macOS
1. Install MacTeX: https://www.tug.org/mactex/
2. Update PATH in `~/.zshrc` or `~/.bash_profile`:
   ```bash
   export PATH="/usr/local/texlive/2024/bin/universal-darwin:$PATH"
   ```
3. Install packages:
   ```bash
   sudo tlmgr install lato fontawesome5 titlesec
   ```

### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install -y texlive-latex-base texlive-fonts-recommended texlive-fonts-extra texlive-latex-extra
```

## Docker Setup

### Dockerfile for Backend with LaTeX
```dockerfile
FROM python:3.13-slim

# Install LaTeX and required packages
RUN apt-get update && apt-get install -y \
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-latex-extra \
    texlive-xetex \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
WORKDIR /app
COPY pyproject.toml .
RUN pip install uv && uv pip install --system -e .

# Copy application
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Render.com Deployment

### render.yaml
```yaml
services:
  - type: web
    name: resume-twin-backend
    env: python
    buildCommand: |
      apt-get update
      apt-get install -y texlive-latex-base texlive-fonts-recommended texlive-fonts-extra texlive-latex-extra
      pip install uv
      uv pip install --system -e .
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.13.5
```

## Vercel/Railway Alternative (Without LaTeX)

If LaTeX cannot be installed, use these fallback options:

### Option 1: External LaTeX API
Use Overleaf API or similar services for PDF generation.

### Option 2: HTML to PDF
```python
# Install weasyprint
pip install weasyprint

# Convert HTML to PDF instead of LaTeX
from weasyprint import HTML

def generate_pdf_from_html(html_content):
    pdf_bytes = HTML(string=html_content).write_pdf()
    return pdf_bytes
```

### Option 3: Server less Function
Deploy LaTeX compilation as a separate serverless function on AWS Lambda with custom runtime.

## Testing LaTeX Installation

Run this test script:

```python
import subprocess

def test_latex_installation():
    try:
        result = subprocess.run(
            ['pdflatex', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✓ LaTeX is installed correctly")
            print(result.stdout.split('\n')[0])
            return True
        else:
            print("✗ LaTeX installation error")
            return False
    except FileNotFoundError:
        print("✗ pdflatex not found in PATH")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    test_latex_installation()
```

## Required LaTeX Packages

Minimum packages needed for professional_resume.tex:
- `lato` - Lato font family
- `fontawesome5` - FontAwesome icons
- `geometry` - Page layout
- `hyperref` - Hyperlinks
- `enumitem` - List formatting
- `titlesec` - Section formatting
- `xcolor` - Colors

## Troubleshooting

### Issue: pdflatex not found
**Solution**: Ensure LaTeX bin directory is in PATH

### Issue: Missing font packages
**Solution**: Install texlive-fonts-extra package

### Issue: Compilation timeout
**Solution**: Increase timeout in latex_service.py (currently 60 seconds)

### Issue: Permission denied
**Solution**: Ensure temp directory has write permissions

## Performance Optimization

1. **Use pdflatex with nonstopmode**: Already implemented
2. **Limit compilation passes**: Currently set to 2 passes
3. **Cache compiled PDFs**: Store in S3/storage
4. **Pre-compile templates**: Generate template previews once

## Security Considerations

1. **Sanitize user input**: Prevent LaTeX injection attacks
2. **Limit file size**: Set maximum input size
3. **Timeout compilations**: Prevent infinite loops
4. **Isolate processes**: Run in containers/sandboxes
5. **Validate templates**: Only allow approved templates
