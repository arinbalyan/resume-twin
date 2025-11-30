# Resume Twin - Database Architecture Documentation

## Overview

This document provides comprehensive documentation of the Resume Twin database architecture, including entity relationships, schema descriptions, data flow diagrams, and access control policies.

## Table of Contents

1. [Database Overview](#database-overview)
2. [Entity Relationship Diagram](#entity-relationship-diagram)
3. [PDF Storage Architecture](#pdf-storage-architecture)
4. [Table Descriptions](#table-descriptions)
5. [Access Control & Security](#access-control--security)
6. [Data Flow Diagrams](#data-flow-diagrams)
7. [API Integration](#api-integration)

---

## Database Overview

Resume Twin uses **PostgreSQL** via **Supabase** as its primary database. The system is designed for:

- **User Profile Management**: Store professional information, education, and experience
- **Project Portfolio**: Manage tagged project portfolios for resume customization  
- **Resume Generation**: Template-based resume creation with AI optimization
- **Secure PDF Storage**: User-owned PDFs stored in Supabase Storage (S3-compatible)

### Technology Stack

| Component | Technology |
|-----------|------------|
| Database | PostgreSQL 15+ (Supabase) |
| Storage | Supabase Storage (S3-compatible) |
| Authentication | Supabase Auth (JWT) |
| Row-Level Security | PostgreSQL RLS Policies |

---

## Entity Relationship Diagram

```mermaid
erDiagram
    direction TB
    
    %% Core User Tables
    profiles ||--o{ education : "has"
    profiles ||--o{ projects : "owns"
    profiles ||--o{ certifications : "has"
    profiles ||--o{ internships : "has"
    profiles ||--o{ courses : "completed"
    profiles ||--o{ activities : "participates"
    profiles ||--o{ resume_versions : "creates"
    profiles ||--o{ generated_pdfs : "owns"
    profiles ||--o{ file_uploads : "uploads"
    
    %% Project Relationships
    projects ||--o{ project_media : "contains"
    projects ||--o{ project_technologies : "uses"
    
    %% Resume Relationships
    templates ||--o{ resume_versions : "used_in"
    templates ||--o{ template_ratings : "rated_by"
    resume_versions ||--o{ optimization_history : "optimized"
    resume_versions ||--o{ generated_pdfs : "generates"
    
    %% PDF Relationships
    generated_pdfs ||--o{ pdf_download_logs : "tracked_by"
    
    %% Entity Definitions
    profiles {
        uuid id PK
        text email UK
        text full_name
        text phone
        text city
        text country
        text linkedin_url
        text github_url
        text portfolio_url
        text bio
        text current_title
        int experience_years
        boolean is_public
        timestamp created_at
        timestamp updated_at
    }
    
    projects {
        uuid id PK
        uuid user_id FK
        text title
        text description
        jsonb bullet_points
        text category
        jsonb tags
        jsonb technologies
        text status
        boolean is_featured
        boolean is_public
        timestamp created_at
    }
    
    generated_pdfs {
        uuid id PK
        uuid user_id FK
        uuid resume_version_id FK
        text file_name
        text storage_path UK
        bigint file_size
        text template_name
        text generation_method
        text generation_status
        boolean is_public
        uuid public_token
        int download_count
        timestamp expires_at
        timestamp created_at
    }
    
    pdf_download_logs {
        uuid id PK
        uuid pdf_id FK
        uuid user_id FK
        inet ip_address
        text download_type
        timestamp downloaded_at
    }
    
    resume_versions {
        uuid id PK
        uuid user_id FK
        uuid template_id FK
        text title
        text job_description
        jsonb selected_project_ids
        jsonb selected_tags
        text pdf_url
        text status
        boolean is_default
        int optimization_score
        timestamp created_at
    }
    
    templates {
        uuid id PK
        text name
        text category
        text latex_content
        text css_styles
        boolean is_public
        boolean is_featured
        int download_count
        decimal rating
        timestamp created_at
    }
    
    education {
        uuid id PK
        uuid user_id FK
        text institution
        text degree
        text field_of_study
        int graduation_year
        boolean is_featured
    }
```

---

## PDF Storage Architecture

### Storage Flow Diagram

```mermaid
flowchart TB
    subgraph "Client"
        A["User Request<br/>Generate PDF"]
    end
    
    subgraph "Backend API"
        B["POST /api/v1/pdfs/generate"]
        C["Template Service<br/>Load & Render HTML"]
        D["HTML-to-PDF Service<br/>Cloud Generation"]
        E["PDF Storage Service<br/>Store & Track"]
    end
    
    subgraph "External Services"
        F["PDFShift API"]
        G["Browserless API"]
        H["HTML2PDF API"]
    end
    
    subgraph "Supabase"
        I[("Storage Bucket<br/>resumes/{user_id}/")]
        J[("Database<br/>generated_pdfs table")]
    end
    
    subgraph "Download Flow"
        K["GET /api/v1/pdfs/{id}/download"]
        L["Verify Ownership"]
        M["Generate Presigned URL"]
        N["Stream PDF to User"]
    end
    
    A --> B
    B --> C
    C --> D
    D --> F & G & H
    F & G & H --> E
    E --> I
    E --> J
    
    K --> L
    L --> M
    M --> I
    I --> N
    
    style I fill:#ffd700,stroke:#333
    style J fill:#4169e1,stroke:#333
    style F fill:#90EE90,stroke:#333
    style G fill:#90EE90,stroke:#333
    style H fill:#90EE90,stroke:#333
```

### Storage Path Convention

```
resumes/
├── {user_id_1}/
│   ├── {pdf_id_1}.pdf
│   ├── {pdf_id_2}.pdf
│   └── {pdf_id_3}.pdf
├── {user_id_2}/
│   ├── {pdf_id_4}.pdf
│   └── {pdf_id_5}.pdf
└── ...
```

**Path Format**: `resumes/{user_id}/{pdf_id}.pdf`

This structure ensures:
- User isolation at the folder level
- Easy cleanup when user is deleted
- Efficient listing of user's PDFs
- RLS policies can verify ownership via path

---

## Table Descriptions

### Core Tables

#### `generated_pdfs`

Stores metadata for all PDFs generated by users.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | UUID | No | Primary key, auto-generated |
| `user_id` | UUID | No | FK to profiles.id - **owner of the PDF** |
| `resume_version_id` | UUID | Yes | FK to resume_versions.id (optional link) |
| `file_name` | TEXT | No | Display name: "John_Doe_Resume.pdf" |
| `storage_path` | TEXT | No | S3 path: "resumes/{user_id}/{pdf_id}.pdf" |
| `file_size` | BIGINT | No | Size in bytes |
| `mime_type` | TEXT | Yes | Default: "application/pdf" |
| `template_name` | TEXT | Yes | Template used (e.g., "modern_resume") |
| `template_type` | TEXT | Yes | "html" or "latex" |
| `generation_method` | TEXT | No | "pdfshift", "browserless", "html2pdf", "weasyprint" |
| `generation_time_ms` | INTEGER | Yes | Generation time in milliseconds |
| `generation_status` | TEXT | Yes | "pending", "generating", "completed", "failed" |
| `error_message` | TEXT | Yes | Error details if generation failed |
| `content_hash` | TEXT | Yes | SHA-256 hash for deduplication |
| `is_public` | BOOLEAN | Yes | Default: false - allows public sharing |
| `public_token` | UUID | Yes | Token for public sharing URL |
| `download_count` | INTEGER | Yes | Default: 0 - tracks downloads |
| `last_downloaded_at` | TIMESTAMPTZ | Yes | Last download timestamp |
| `expires_at` | TIMESTAMPTZ | Yes | Auto-delete after this time (optional) |
| `created_at` | TIMESTAMPTZ | Yes | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | Yes | Last update timestamp |

**Indexes**:
- `idx_generated_pdfs_user_id` - Fast lookup by user
- `idx_generated_pdfs_user_created` - User's recent PDFs
- `idx_generated_pdfs_storage_path` - S3 operations
- `idx_generated_pdfs_public_token` - Public sharing (partial index)
- `idx_generated_pdfs_expires_at` - Cleanup expired PDFs (partial index)

#### `pdf_download_logs`

Audit log for all PDF download events.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | UUID | No | Primary key |
| `pdf_id` | UUID | No | FK to generated_pdfs.id |
| `user_id` | UUID | Yes | FK to profiles.id (NULL for public downloads) |
| `ip_address` | INET | Yes | Downloader's IP address |
| `user_agent` | TEXT | Yes | Browser/client info |
| `download_type` | TEXT | Yes | "direct", "presigned_url", "public_link" |
| `downloaded_at` | TIMESTAMPTZ | Yes | Download timestamp |

---

## Access Control & Security

### Row-Level Security (RLS) Policies

All tables use PostgreSQL RLS to enforce access control at the database level.

```mermaid
flowchart LR
    subgraph "Authentication"
        A["JWT Token<br/>(Supabase Auth)"]
    end
    
    subgraph "RLS Policy Check"
        B{"auth.uid() =<br/>user_id?"}
    end
    
    subgraph "Access Granted"
        C["SELECT ✓"]
        D["INSERT ✓"]
        E["UPDATE ✓"]
        F["DELETE ✓"]
    end
    
    subgraph "Access Denied"
        G["403 Forbidden"]
    end
    
    A --> B
    B -->|Yes| C & D & E & F
    B -->|No| G
    
    style C fill:#90EE90
    style D fill:#90EE90
    style E fill:#90EE90
    style F fill:#90EE90
    style G fill:#FF6B6B
```

#### PDF Access Policies

```sql
-- Users can only see their own PDFs
CREATE POLICY "Users can view own PDFs" 
    ON generated_pdfs FOR SELECT 
    USING (auth.uid() = user_id);

-- Users can create PDFs for themselves
CREATE POLICY "Users can create own PDFs" 
    ON generated_pdfs FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

-- Users can update their own PDFs
CREATE POLICY "Users can update own PDFs" 
    ON generated_pdfs FOR UPDATE 
    USING (auth.uid() = user_id);

-- Users can delete their own PDFs
CREATE POLICY "Users can delete own PDFs" 
    ON generated_pdfs FOR DELETE 
    USING (auth.uid() = user_id);

-- Public PDFs can be viewed by anyone
CREATE POLICY "Public PDFs are viewable" 
    ON generated_pdfs FOR SELECT 
    USING (is_public = true);
```

### Supabase Storage Policies

```sql
-- Create the resumes bucket
INSERT INTO storage.buckets (id, name, public)
VALUES ('resumes', 'resumes', false);

-- Users can upload their own PDFs
CREATE POLICY "Users can upload own PDFs"
ON storage.objects FOR INSERT
WITH CHECK (
    bucket_id = 'resumes' 
    AND auth.uid()::text = (storage.foldername(name))[1]
);

-- Users can read their own PDFs
CREATE POLICY "Users can read own PDFs"
ON storage.objects FOR SELECT
USING (
    bucket_id = 'resumes' 
    AND auth.uid()::text = (storage.foldername(name))[1]
);

-- Users can delete their own PDFs
CREATE POLICY "Users can delete own PDFs"
ON storage.objects FOR DELETE
USING (
    bucket_id = 'resumes' 
    AND auth.uid()::text = (storage.foldername(name))[1]
);
```

---

## Data Flow Diagrams

### PDF Generation Flow

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant API as Backend API
    participant TS as Template Service
    participant PDF as PDF Generator
    participant Cloud as Cloud PDF Service
    participant S3 as Supabase Storage
    participant DB as Database
    
    U->>API: POST /pdfs/generate
    Note over U,API: {template_name, file_name}
    
    API->>API: Authenticate (JWT)
    API->>TS: Load template
    TS-->>API: HTML template
    
    API->>TS: Render with user data
    TS-->>API: Rendered HTML
    
    API->>PDF: Generate PDF
    PDF->>Cloud: Send HTML
    Note over Cloud: PDFShift / Browserless
    Cloud-->>PDF: PDF bytes
    PDF-->>API: PDF content
    
    API->>S3: Upload PDF
    Note over S3: resumes/{user_id}/{pdf_id}.pdf
    S3-->>API: Success
    
    API->>DB: Insert metadata
    Note over DB: generated_pdfs table
    DB-->>API: Record created
    
    API-->>U: {pdf_id, download_url}
```

### PDF Download Flow

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant API as Backend API
    participant DB as Database
    participant S3 as Supabase Storage
    
    U->>API: GET /pdfs/{id}/download
    
    API->>API: Authenticate (JWT)
    API->>DB: SELECT * FROM generated_pdfs
    Note over DB: WHERE id = {pdf_id}
    
    DB-->>API: PDF record
    
    alt User owns PDF
        API->>API: Verify auth.uid() = user_id
        API->>S3: Generate presigned URL
        S3-->>API: Presigned URL (1hr expiry)
        
        API->>DB: Log download
        Note over DB: pdf_download_logs
        
        API->>DB: Increment counter
        Note over DB: download_count++
        
        API-->>U: Stream PDF / Redirect URL
    else Not authorized
        API-->>U: 403 Forbidden
    end
```

### Public Sharing Flow

```mermaid
sequenceDiagram
    autonumber
    participant Owner as PDF Owner
    participant API as Backend API
    participant DB as Database
    participant Public as Public User
    participant S3 as Supabase Storage
    
    %% Enable sharing
    Owner->>API: PATCH /pdfs/{id}/public
    Note over Owner,API: {is_public: true}
    
    API->>DB: UPDATE generated_pdfs
    Note over DB: SET is_public = true
    DB-->>API: public_token returned
    
    API-->>Owner: {public_url}
    Note over Owner: Share this URL
    
    %% Public download
    Public->>API: GET /pdfs/public/{token}
    Note over Public,API: No auth required
    
    API->>DB: SELECT * FROM generated_pdfs
    Note over DB: WHERE public_token = {token}<br/>AND is_public = true
    
    DB-->>API: PDF record
    
    API->>S3: Generate presigned URL
    S3-->>API: Presigned URL
    
    API->>DB: Log download
    Note over DB: user_id = NULL
    
    API-->>Public: Redirect to PDF
```

---

## API Integration

### Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/pdfs/generate` | Generate and store PDF | Yes |
| GET | `/api/v1/pdfs/my-pdfs` | List user's PDFs | Yes |
| GET | `/api/v1/pdfs/{id}/download-url` | Get presigned download URL | Yes |
| GET | `/api/v1/pdfs/{id}/download` | Direct PDF download | Yes |
| DELETE | `/api/v1/pdfs/{id}` | Delete a PDF | Yes |
| PATCH | `/api/v1/pdfs/{id}/public` | Toggle public sharing | Yes |
| GET | `/api/v1/pdfs/public/{token}` | Download public PDF | No |
| GET | `/api/v1/pdfs/stats` | Get storage statistics | Yes |

### Example Requests

#### Generate PDF

```bash
curl -X POST "http://localhost:8000/api/v1/pdfs/generate" \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "template_name": "modern_resume",
    "file_name": "John_Doe_Resume.pdf",
    "name": "John Doe",
    "title": "Software Engineer",
    "email": "john@example.com"
  }'
```

#### List User's PDFs

```bash
curl "http://localhost:8000/api/v1/pdfs/my-pdfs?limit=10" \
  -H "Authorization: Bearer <jwt_token>"
```

#### Download PDF

```bash
curl "http://localhost:8000/api/v1/pdfs/{pdf_id}/download" \
  -H "Authorization: Bearer <jwt_token>" \
  -o resume.pdf
```

---

## Maintenance Operations

### Cleanup Expired PDFs

```sql
-- Run periodically to remove expired PDFs
SELECT cleanup_expired_pdfs();
```

### Storage Statistics View

```sql
-- Get user storage summary
SELECT * FROM user_pdf_summary WHERE user_id = 'uuid-here';
```

### Recent Downloads

```sql
-- View recent downloads across all users (admin)
SELECT * FROM recent_pdf_downloads LIMIT 50;
```

---

## Migration Guide

To apply the PDF storage schema:

```bash
# 1. Run the migration
psql $DATABASE_URL -f database/migrations/001_add_generated_pdfs_table.sql

# 2. Create the storage bucket in Supabase Dashboard
# Navigate to Storage > Create new bucket > name: "resumes" > private

# 3. Apply storage policies via Supabase SQL Editor
# (Use the SQL in the migration file under "SUPABASE STORAGE BUCKET POLICY")
```

---

## Related Documentation

- [Supabase Auth Documentation](https://supabase.com/docs/guides/auth)
- [Supabase Storage Documentation](https://supabase.com/docs/guides/storage)
- [PostgreSQL RLS Documentation](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
