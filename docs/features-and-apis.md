# Resume Twin - Feature Guide & Free API Integration

This document explains all the features, free API integrations, and how to get started with Resume Twin.

## 🎯 Overview

Resume Twin is a comprehensive resume generation platform that combines:
- **HTML-to-PDF Generation** - Fast, no-installation-required PDF creation
- **Multiple Professional Templates** - 5 unique, ATS-friendly designs
- **AI-Powered Enhancements** - Using free OpenRouter models
- **GitHub Integration** - Import your projects directly
- **Resume Scoring** - Get instant feedback and ATS compatibility scores

---

## 📄 PDF Generation Methods

Resume Twin supports three PDF generation methods. Choose based on your needs:

### 1. HTML-to-PDF (Recommended for Starting)

```env
PDF_GENERATION_METHOD=html
```

**Pros:**
- No external dependencies
- Fast generation (~1-2 seconds)
- Works in Docker without special setup
- Beautiful templates with CSS styling

**How it works:**
- Uses WeasyPrint library
- Renders HTML templates with Jinja2
- Converts to PDF with proper fonts and styling

### 2. LaTeX (For Maximum Customization)

```env
PDF_GENERATION_METHOD=latex
```

**Pros:**
- Professional typesetting
- Precise layout control
- Industry-standard for academic CVs

**Requirements:**
- texlive installation on server
- More complex Docker setup

### 3. Overleaf API (Cloud-based)

```env
PDF_GENERATION_METHOD=overleaf
OVERLEAF_API_URL=https://api.overleaf.com/v1
OVERLEAF_API_TOKEN=your-token
```

**Pros:**
- No local LaTeX needed
- Always up-to-date LaTeX packages

---

## 🎨 Available Resume Templates

All templates are located in `templates/html/` and support the same data structure:

### 1. Professional Resume (`professional_resume.html`)
- Classic single-column layout
- Yellow and navy color scheme
- Best for traditional industries

### 2. Modern Resume (`modern_resume.html`)
- Two-column layout with sidebar
- Inter font family
- Skills displayed in sidebar

### 3. Creative Resume (`creative_resume.html`)
- Navy sidebar with initials avatar
- Skill bars with progress visualization
- Great for design-oriented roles

### 4. Minimal Resume (`minimal_resume.html`)
- Clean, typography-focused
- Crimson Pro serif headings
- Best for content-heavy resumes

### 5. Developer Resume (`developer_resume.html`)
- GitHub-inspired dark theme
- Stats bar with project count
- Tech tags and code styling
- Perfect for software engineers

---

## 🆓 Free API Integrations

All APIs listed below have FREE tiers - no payment required!

### 1. GitHub API
**Rate Limit:** 5,000 requests/hour (with token), 60/hour (without)

**Features:**
- Fetch user profile and bio
- Import repositories as projects
- Get contribution statistics
- Calculate top programming languages

**How to Get Token:**
1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. No scopes needed for public repos
4. Copy token (starts with `ghp_`)

```env
GITHUB_TOKEN=ghp_your_token_here
```

**API Endpoints:**
- `GET /api/v1/profiles/github/{username}` - Full profile
- `GET /api/v1/profiles/github/{username}/repos` - Repositories
- `POST /api/v1/profiles/github/{username}/import-projects` - Import as resume projects

### 2. OpenRouter AI
**Free Models Available:**
- `openai/gpt-oss-20b:free`
- `meta-llama/llama-3-8b-instruct:free`
- `mistralai/mistral-7b-instruct:free`

**How to Get Key:**
1. Go to [openrouter.ai/keys](https://openrouter.ai/keys)
2. Sign up with email
3. Copy your API key

```env
OPENROUTER_API_KEY=sk-or-your-key-here
OPENROUTER_MODEL=openai/gpt-oss-20b:free
```

### 3. Hunter.io (Email Verification)
**Free Tier:** 50 verifications/month

**How to Get Key:**
1. Go to [hunter.io/api](https://hunter.io/api)
2. Create free account
3. Copy API key from dashboard

```env
HUNTER_API_KEY=your_key_here
```

### 4. Abstract API (Email Validation)
**Free Tier:** 100 requests/month

**How to Get Key:**
1. Go to [abstractapi.com/email-validation-api](https://www.abstractapi.com/email-validation-api)
2. Sign up for free
3. Get key from dashboard

```env
ABSTRACT_EMAIL_API_KEY=your_key_here
```

### 5. IPInfo (Location Detection)
**Free Tier:** 50,000 requests/month

**How to Get Token:**
1. Go to [ipinfo.io/signup](https://ipinfo.io/signup)
2. Sign up with email
3. Token shown on dashboard

```env
IPINFO_TOKEN=your_token_here
```

### 6. Unsplash (Free Images)
**Free Tier:** 50 requests/hour

**How to Get Key:**
1. Go to [unsplash.com/developers](https://unsplash.com/developers)
2. Create an application
3. Copy Access Key

```env
UNSPLASH_ACCESS_KEY=your_key_here
```

### 7. Clearbit (Company Logos)
**100% Free for Logos!**

No API key needed for logos. Use directly:
```
https://logo.clearbit.com/google.com
https://logo.clearbit.com/microsoft.com
```

---

## 📊 Resume Scoring & ATS Checker

Built-in resume scoring with NO API required!

**Features:**
- Overall score (0-100)
- Category scores (Contact, Summary, Experience, Skills, Projects, Education)
- ATS compatibility score
- Actionable suggestions
- Job description keyword matching

**API Endpoint:**
```
POST /api/v1/profiles/score-resume
```

**Request Body:**
```json
{
  "resume_data": {
    "user_name": "John Doe",
    "summary": "...",
    "experience": [...],
    "skills": {...}
  },
  "job_description": "Optional: paste job description for keyword matching"
}
```

---

## 🚀 Quick Start

### 1. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy and configure .env
cp .env.example .env
# Edit .env with your API keys

# Run server
uvicorn app.main:app --reload
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 3. Test the APIs

**List Templates:**
```bash
curl http://localhost:8000/api/v1/templates/
```

**Preview Template as PDF:**
```bash
curl http://localhost:8000/api/v1/templates/professional_resume/preview/pdf > preview.pdf
```

**Get GitHub Profile:**
```bash
curl http://localhost:8000/api/v1/profiles/github/torvalds
```

**Score Resume:**
```bash
curl -X POST http://localhost:8000/api/v1/profiles/score-resume \
  -H "Content-Type: application/json" \
  -d '{"resume_data": {"user_name": "Test User", "summary": "A developer"}}'
```

---

## 📁 Project Structure

```
resume_twin/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/
│   │   │   ├── templates.py     # Template preview & listing
│   │   │   ├── profiles.py      # GitHub & scoring APIs
│   │   │   └── resume.py        # PDF generation
│   │   ├── services/
│   │   │   ├── html_to_pdf_service.py
│   │   │   ├── github_service.py
│   │   │   └── resume_scorer_service.py
│   │   └── core/
│   │       └── config.py        # All settings
│   └── .env.example             # Documented config
├── templates/
│   └── html/
│       ├── professional_resume.html
│       ├── modern_resume.html
│       ├── creative_resume.html
│       ├── minimal_resume.html
│       └── developer_resume.html
└── frontend/
    └── src/
        └── data/
            └── projectTemplates.ts  # Sample projects
```

---

## 💡 Suggestions for Enhancement

### Future Free APIs to Consider:

1. **Groq** - Very fast AI inference (free tier)
   - https://console.groq.com

2. **Together.ai** - $25 free credit for AI
   - https://api.together.xyz

3. **Google Custom Search** - 100 free searches/day
   - For job posting lookups

4. **LinkedIn Scraping** - Via RapidAPI free tier
   - Import LinkedIn profile data

5. **Notion API** - Free for personal use
   - Sync projects from Notion databases

### Potential Features:

1. **Resume Version History** - Track changes over time
2. **One-Click Apply** - Auto-fill job applications
3. **Interview Prep** - AI-generated questions based on resume
4. **Cover Letter Generator** - Match resume to job description
5. **LinkedIn Profile Optimizer** - Sync and improve

---

## 🔧 Troubleshooting

### PDF Generation Issues

**"WeasyPrint not found"**
```bash
pip install weasyprint
# On Ubuntu: apt-get install libpango-1.0-0 libpangocairo-1.0-0
```

**"Font not rendering correctly"**
- Templates use Google Fonts (loaded via @import)
- Ensure internet access during PDF generation

### GitHub API Rate Limiting

**"403 Rate limit exceeded"**
- Add `GITHUB_TOKEN` to .env
- With token: 5,000 requests/hour

### Template Not Found

- Ensure templates are in `templates/html/`
- File extension must be `.html`
- Template name in API excludes extension

---

## 📞 Support

For issues or feature requests, please open a GitHub issue.

Happy Resume Building! 🎉
