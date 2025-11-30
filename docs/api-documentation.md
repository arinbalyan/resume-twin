# Resume Twin Platform - API Documentation

## Overview

The Resume Twin API is a RESTful API built with FastAPI that provides comprehensive endpoints for profile management, AI-powered resume optimization, and portfolio management.

**Base URL**: `https://api.your-domain.com/api/v1`

**API Version**: 1.0.0

## Authentication

All authenticated endpoints require a valid JWT token in the Authorization header:

```http
Authorization: Bearer <your-jwt-token>
```

### Obtain Token

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your-password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

## API Endpoints

### Health Check

#### GET /health

Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production",
  "database": "connected"
}
```

---

## Profile Management

### Get User Profile

#### GET /profiles/{profile_id}

Get a specific user profile.

**Parameters:**
- `profile_id` (path, required): UUID of the profile

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "current_title": "Senior Software Engineer",
  "city": "San Francisco",
  "country": "USA",
  "bio": "Experienced software engineer...",
  "experience_years": 5,
  "linkedin_url": "https://linkedin.com/in/johndoe",
  "github_url": "https://github.com/johndoe",
  "is_public": true,
  "profile_completion_score": 85,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-20T14:45:00Z"
}
```

### Create Profile

#### POST /profiles

Create a new user profile.

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "full_name": "Jane Smith",
  "phone": "+1234567890",
  "city": "New York",
  "country": "USA",
  "current_title": "Full Stack Developer",
  "bio": "Passionate developer with...",
  "experience_years": 3,
  "preferred_job_types": ["full-time", "remote"],
  "target_industries": ["technology", "fintech"],
  "willing_to_relocate": true,
  "is_public": true
}
```

**Response:** 201 Created
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "email": "newuser@example.com",
  ...
}
```

### Update Profile

#### PUT /profiles/{profile_id}

Update an existing profile.

**Request Body:**
```json
{
  "bio": "Updated bio...",
  "current_title": "Lead Software Engineer",
  "experience_years": 6
}
```

**Response:** 200 OK

### Delete Profile

#### DELETE /profiles/{profile_id}

Delete a user profile.

**Response:** 204 No Content

---

## Education Management

### Get User Education

#### GET /education?user_id={user_id}

Get all education entries for a user.

**Query Parameters:**
- `user_id` (required): User UUID
- `limit` (optional, default: 50): Results per page
- `offset` (optional, default: 0): Pagination offset

**Response:**
```json
[
  {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "institution": "Stanford University",
    "degree": "Bachelor of Science",
    "field_of_study": "Computer Science",
    "cgpa": 3.8,
    "graduation_year": 2020,
    "location": "Stanford, CA",
    "start_date": "2016-09-01",
    "end_date": "2020-05-15",
    "is_current": false,
    "is_featured": true,
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

### Create Education Entry

#### POST /education?user_id={user_id}

Add education entry to profile.

**Request Body:**
```json
{
  "institution": "MIT",
  "degree": "Master of Science",
  "field_of_study": "Artificial Intelligence",
  "cgpa": 3.9,
  "graduation_year": 2022,
  "location": "Cambridge, MA",
  "start_date": "2020-09-01",
  "end_date": "2022-05-20",
  "description": "Specialized in machine learning...",
  "is_current": false,
  "is_featured": true
}
```

**Response:** 201 Created

### Update Education Entry

#### PUT /education/{education_id}

Update education entry.

**Response:** 200 OK

### Delete Education Entry

#### DELETE /education/{education_id}

Delete education entry.

**Response:** 204 No Content

---

## Experience Management

### Certifications

#### GET /experience/certifications?user_id={user_id}

Get all certifications for a user.

**Response:**
```json
[
  {
    "id": "880e8400-e29b-41d4-a716-446655440003",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "AWS Certified Solutions Architect",
    "issuer": "Amazon Web Services",
    "issue_date": "2023-01-15",
    "expiry_date": "2026-01-15",
    "credential_id": "AWS-12345",
    "verification_url": "https://aws.amazon.com/verify/12345",
    "skills_acquired": ["AWS", "Cloud Architecture", "Security"],
    "is_verified": true,
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

#### POST /experience/certifications?user_id={user_id}

Create certification entry.

**Request Body:**
```json
{
  "name": "Google Cloud Professional Architect",
  "issuer": "Google Cloud",
  "issue_date": "2023-06-01",
  "expiry_date": "2025-06-01",
  "credential_id": "GCP-67890",
  "verification_url": "https://googlecloud.com/verify/67890",
  "skills_acquired": ["GCP", "Kubernetes", "Terraform"]
}
```

**Response:** 201 Created

### Internships

#### GET /experience/internships?user_id={user_id}

Get all internships.

**Response:**
```json
[
  {
    "id": "990e8400-e29b-41d4-a716-446655440004",
    "company": "Tech Corp",
    "role": "Software Engineering Intern",
    "location": "San Francisco, CA",
    "start_date": "2019-06-01",
    "end_date": "2019-08-31",
    "is_current": false,
    "description": "Developed features for...",
    "achievements": [
      "Built REST API serving 1M requests/day",
      "Improved test coverage from 60% to 85%"
    ],
    "key_learnings": ["Microservices", "Docker", "CI/CD"],
    "team_size": 5,
    "project_count": 3
  }
]
```

#### POST /experience/internships?user_id={user_id}

Create internship entry.

### Courses

#### GET /experience/courses?user_id={user_id}

Get all courses.

#### POST /experience/courses?user_id={user_id}

Create course entry.

### Activities

#### GET /experience/activities?user_id={user_id}

Get all activities.

#### POST /experience/activities?user_id={user_id}

Create activity entry.

### Experience Summary

#### GET /experience/summary?user_id={user_id}

Get comprehensive experience summary.

**Response:**
```json
{
  "certifications": [...],
  "internships": [...],
  "courses": [...],
  "activities": [...],
  "total_experience_items": 12,
  "unique_skills_acquired": ["Python", "AWS", "React", ...]
}
```

---

## Project Management

### Get User Projects

#### GET /projects?user_id={user_id}

Get all projects for a user.

**Query Parameters:**
- `user_id` (required): User UUID
- `category` (optional): Filter by category
- `status` (optional): Filter by status (draft, in_progress, completed, on_hold)
- `is_featured` (optional): Filter featured projects
- `limit` (optional, default: 20)
- `offset` (optional, default: 0)

**Response:**
```json
[
  {
    "id": "aa0e8400-e29b-41d4-a716-446655440005",
    "title": "E-Commerce Platform",
    "short_description": "Full-stack e-commerce solution",
    "category": "Web Development",
    "technologies": ["React", "FastAPI", "PostgreSQL", "Docker"],
    "github_url": "https://github.com/user/ecommerce",
    "live_url": "https://ecommerce-demo.com",
    "status": "completed",
    "is_featured": true,
    "created_at": "2024-01-15T10:30:00Z",
    "media_count": 5,
    "technology_count": 8
  }
]
```

### Create Project

#### POST /projects?user_id={user_id}

Create a new project.

**Request Body:**
```json
{
  "title": "Task Management API",
  "description": "RESTful API for task management with authentication and real-time updates",
  "short_description": "Task management API with real-time features",
  "category": "Backend Development",
  "technologies": ["Python", "FastAPI", "WebSockets", "Redis"],
  "github_url": "https://github.com/user/task-api",
  "live_url": "https://task-api-demo.com",
  "start_date": "2023-01-01",
  "end_date": "2023-06-30",
  "status": "completed",
  "is_featured": true,
  "difficulty_level": 4,
  "team_size": 1,
  "impact_metrics": {
    "users": 1000,
    "requests_per_day": 50000
  }
}
```

**Response:** 201 Created

### Get Project Details

#### GET /projects/{project_id}

Get complete project details including media and technologies.

**Response:**
```json
{
  "id": "aa0e8400-e29b-41d4-a716-446655440005",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "E-Commerce Platform",
  "description": "Full description...",
  "category": "Web Development",
  "technologies": ["React", "FastAPI", "PostgreSQL"],
  "github_url": "https://github.com/user/ecommerce",
  "live_url": "https://ecommerce-demo.com",
  "status": "completed",
  "media": [
    {
      "id": "bb0e8400-e29b-41d4-a716-446655440006",
      "file_url": "https://storage.supabase.co/v1/object/...",
      "file_name": "homepage.png",
      "media_type": "image/png",
      "caption": "Homepage screenshot",
      "is_cover_image": true,
      "display_order": 0
    }
  ],
  "technologies": [
    {
      "id": "cc0e8400-e29b-41d4-a716-446655440007",
      "technology_name": "React",
      "technology_category": "Frontend",
      "proficiency_level": 5,
      "is_primary": true
    }
  ]
}
```

### Upload Project Media

#### POST /projects/{project_id}/media

Upload media file for a project.

**Request:**
```http
POST /projects/{project_id}/media
Content-Type: multipart/form-data

file: [binary file data]
caption: "Homepage screenshot"
alt_text: "E-commerce homepage showing featured products"
is_cover_image: true
```

**Response:** 201 Created

### Add Project Technology

#### POST /projects/{project_id}/technologies

Add technology to a project.

**Request Body:**
```json
{
  "technology_name": "Docker",
  "technology_category": "DevOps",
  "proficiency_level": 4,
  "is_primary": false
}
```

**Response:** 201 Created

---

## AI-Powered Resume Optimization

### Analyze Job Description

#### POST /ai/analyze-job

Analyze a job description to extract requirements and keywords.

**Request Body:**
```json
{
  "job_description": "We are seeking a Senior Full-Stack Developer...",
  "extract_keywords": true
}
```

**Response:**
```json
{
  "success": true,
  "analysis": {
    "job_title": "Senior Full-Stack Developer",
    "company": "Tech Corp",
    "skills": ["Python", "React", "FastAPI", "PostgreSQL", "Docker"],
    "keywords": ["scalable", "microservices", "API", "cloud", "agile"],
    "experience_level": "senior",
    "education_requirements": ["Bachelor's in Computer Science"],
    "responsibilities": [
      "Design and implement scalable applications",
      "Mentor junior developers"
    ],
    "requirements": [
      {
        "category": "technical_skill",
        "skill": "Python",
        "importance": "required",
        "years_experience": 5
      }
    ]
  },
  "message": "Successfully analyzed job posting for Senior Full-Stack Developer"
}
```

### Optimize Resume

#### POST /ai/optimize-resume

Optimize resume content for a specific job.

**Request Body:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "job_description": "Senior Full-Stack Developer position...",
  "optimization_level": "standard",
  "include_suggestions": true
}
```

**Optimization Levels:**
- `basic`: Quick keyword matching
- `standard`: Detailed optimization with ATS compliance
- `advanced`: Deep analysis with personalized suggestions

**Response:**
```json
{
  "success": true,
  "optimization": {
    "match_score": 85.5,
    "ats_compatibility_score": 90.0,
    "missing_skills": ["Kubernetes", "AWS"],
    "matching_skills": ["Python", "React", "FastAPI", "PostgreSQL", "Docker"],
    "keyword_suggestions": [
      "microservices architecture",
      "scalable systems",
      "RESTful APIs"
    ],
    "content_improvements": [
      {
        "section": "experience",
        "suggestion": "Add metrics to quantify achievements (e.g., 'Improved response time by 40%')"
      },
      {
        "section": "projects",
        "suggestion": "Highlight scalability aspects of your e-commerce platform"
      }
    ],
    "formatting_suggestions": [
      "Use action verbs at the start of bullet points",
      "Include quantifiable achievements",
      "Add a technical skills section"
    ]
  },
  "job_match_score": 85.5,
  "ats_score": 90.0,
  "message": "Resume optimized for Senior Full-Stack Developer position"
}
```

### AI Service Health Check

#### GET /ai/health

Check AI service status and circuit breaker state.

**Response:**
```json
{
  "service": "ai_optimization",
  "status": "healthy",
  "circuit_breaker_state": "closed"
}
```

**Status Values:**
- `healthy`: Service operating normally
- `degraded`: Service experiencing issues
- `recovering`: Service recovering from failures

**Circuit Breaker States:**
- `closed`: Normal operation
- `open`: Service temporarily disabled due to failures
- `half_open`: Testing recovery

---

## Templates

### Get Templates

#### GET /templates

Get available resume templates.

### Get Template

#### GET /templates/{template_id}

Get specific template details.

### Create Custom Template

#### POST /templates

Create custom template (admin only).

---

## Resume Generation

### Generate Resume

#### POST /resume/generate

Generate PDF resume from profile data.

### Get Resume Versions

#### GET /resume?user_id={user_id}

Get all resume versions for a user.

### Download Resume

#### GET /resume/{resume_id}/download

Download resume PDF.

---

## File Management

### Upload File

#### POST /files/upload

Upload file (certificate, portfolio item, etc.).

**Request:**
```http
POST /files/upload
Content-Type: multipart/form-data

file: [binary file data]
user_id: "550e8400-e29b-41d4-a716-446655440000"
category: "certificate"
```

**Response:**
```json
{
  "id": "dd0e8400-e29b-41d4-a716-446655440008",
  "file_url": "https://storage.supabase.co/v1/object/...",
  "file_name": "aws-certificate.pdf",
  "file_size": 524288,
  "mime_type": "application/pdf",
  "category": "certificate",
  "upload_status": "completed",
  "virus_scan_status": "clean"
}
```

---

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid request data",
  "error_code": "VALIDATION_ERROR"
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication required"
}
```

### 403 Forbidden
```json
{
  "detail": "Permission denied"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error",
  "error_code": "INTERNAL_ERROR"
}
```

### 503 Service Unavailable
```json
{
  "detail": "AI service temporarily unavailable",
  "error_code": "AI_SERVICE_UNAVAILABLE"
}
```

---

## Rate Limiting

API endpoints are rate-limited:
- **Standard tier**: 100 requests/minute, 1000 requests/hour
- **Premium tier**: 1000 requests/minute, 10000 requests/hour

Rate limit headers:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

---

## Pagination

List endpoints support pagination:

**Query Parameters:**
- `limit`: Results per page (default: 20, max: 100)
- `offset`: Number of results to skip

**Response Headers:**
```http
X-Total-Count: 150
X-Page-Size: 20
Link: </api/v1/projects?limit=20&offset=20>; rel="next"
```

---

## Versioning

API version is specified in the URL: `/api/v1/`

Major version changes will be backwards-incompatible and announced in advance.

---

## Interactive Documentation

- **Swagger UI**: https://api.your-domain.com/docs
- **ReDoc**: https://api.your-domain.com/redoc
- **OpenAPI Spec**: https://api.your-domain.com/openapi.json

---

## Support

- **GitHub Issues**: https://github.com/your-org/resume-twin/issues
- **Email**: api-support@your-domain.com
- **Documentation**: https://docs.your-domain.com

---

**Last Updated**: November 30, 2025
**API Version**: 1.0.0
