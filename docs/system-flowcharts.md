# Resume Twin - System Flowcharts

## Table of Contents

1. [System Overview](#system-overview)
2. [User Authentication Flow](#user-authentication-flow)
3. [Resume Generation Pipeline](#resume-generation-pipeline)
4. [PDF Storage & Retrieval](#pdf-storage--retrieval)
5. [Project Management Flow](#project-management-flow)
6. [AI Optimization Flow](#ai-optimization-flow)

---

## System Overview

### High-Level Architecture

```mermaid
flowchart TB
    subgraph "Frontend (React + Vite)"
        UI["User Interface"]
        Auth["Auth Context"]
        Forms["Resume Forms"]
    end
    
    subgraph "Backend (FastAPI)"
        API["API Gateway"]
        Services["Service Layer"]
        subgraph "Core Services"
            TS["Template Service"]
            PS["PDF Storage"]
            AS["AI Service"]
            PJS["Project Service"]
        end
    end
    
    subgraph "External APIs"
        PDF["PDF Generation<br/>(PDFShift/Browserless)"]
        AI["OpenRouter AI"]
        GH["GitHub API"]
    end
    
    subgraph "Supabase"
        SAuth["Auth Service"]
        DB[("PostgreSQL")]
        S3[("Storage<br/>S3-compatible")]
    end
    
    UI --> API
    Auth --> SAuth
    API --> Services
    Services --> TS & PS & AS & PJS
    PS --> S3
    PS --> PDF
    AS --> AI
    PJS --> GH
    Services --> DB
    SAuth --> DB
    
    style S3 fill:#ffd700
    style DB fill:#4169e1
    style PDF fill:#90EE90
```

---

## User Authentication Flow

### Login Process

```mermaid
flowchart TD
    A["User Opens App"] --> B{"Already<br/>Logged In?"}
    B -->|Yes| C["Redirect to Dashboard"]
    B -->|No| D["Show Login Page"]
    
    D --> E["Enter Credentials"]
    E --> F["Submit Login"]
    F --> G["Supabase Auth"]
    
    G --> H{"Valid<br/>Credentials?"}
    H -->|Yes| I["Generate JWT"]
    H -->|No| J["Show Error"]
    
    I --> K["Store in Context"]
    K --> L["Create/Update Profile"]
    L --> C
    
    J --> E
    
    style C fill:#90EE90
    style J fill:#FF6B6B
```

### Registration Process

```mermaid
flowchart TD
    A["Click Register"] --> B["Enter Email & Password"]
    B --> C["Submit Registration"]
    C --> D["Supabase signUp"]
    
    D --> E{"Email<br/>Already Exists?"}
    E -->|Yes| F["Show Error"]
    E -->|No| G["Create Auth User"]
    
    G --> H["Send Verification Email"]
    H --> I["Create Profile Record"]
    I --> J["Show Success Message"]
    
    J --> K["Wait for Email Verification"]
    K --> L["User Clicks Link"]
    L --> M["Verify & Redirect to Login"]
    
    F --> B
    
    style J fill:#90EE90
    style F fill:#FF6B6B
```

---

## Resume Generation Pipeline

### Complete Generation Flow

```mermaid
flowchart TB
    subgraph "Step 1: Template Selection"
        A["Browse Templates"] --> B["Preview Template"]
        B --> C["Select Template"]
    end
    
    subgraph "Step 2: Data Collection"
        C --> D["Load User Profile"]
        D --> E["Select Projects"]
        E --> F["Filter by Tags"]
        F --> G["Add Experience"]
        G --> H["Review Content"]
    end
    
    subgraph "Step 3: AI Optimization"
        H --> I{"Enable AI?"}
        I -->|Yes| J["Enter Job Description"]
        J --> K["AI Analyzes JD"]
        K --> L["Extract Keywords"]
        L --> M["Optimize Content"]
        M --> N["Calculate ATS Score"]
        I -->|No| O["Skip Optimization"]
    end
    
    subgraph "Step 4: PDF Generation"
        N --> P["Render HTML"]
        O --> P
        P --> Q["Send to PDF Service"]
        Q --> R{"Generation<br/>Success?"}
        R -->|Yes| S["Upload to Storage"]
        R -->|No| T["Show Error"]
        S --> U["Save Metadata to DB"]
        U --> V["Return Download URL"]
    end
    
    subgraph "Step 5: Download"
        V --> W["Preview PDF"]
        W --> X["Download PDF"]
    end
    
    style V fill:#90EE90
    style T fill:#FF6B6B
```

### PDF Generation Methods

```mermaid
flowchart LR
    subgraph "Input"
        HTML["Rendered HTML"]
    end
    
    subgraph "Cloud Services (Primary)"
        PS["PDFShift<br/>250 free/month"]
        BL["Browserless<br/>1000 free/month"]
        H2P["HTML2PDF<br/>100 free/month"]
    end
    
    subgraph "Local (Fallback)"
        WP["WeasyPrint<br/>(Requires GTK)"]
    end
    
    subgraph "Output"
        PDF["PDF Bytes"]
    end
    
    HTML --> PS & BL & H2P
    HTML --> WP
    PS & BL & H2P --> PDF
    WP --> PDF
    
    style PS fill:#90EE90
    style BL fill:#90EE90
    style H2P fill:#90EE90
    style WP fill:#FFD700
```

---

## PDF Storage & Retrieval

### Storage Flow

```mermaid
flowchart TD
    A["PDF Generated"] --> B["Compute SHA-256 Hash"]
    B --> C["Generate Storage Path"]
    C --> D["resumes/{user_id}/{pdf_id}.pdf"]
    
    D --> E["Upload to S3"]
    E --> F{"Upload<br/>Success?"}
    
    F -->|Yes| G["Create DB Record"]
    F -->|No| H["Return Error"]
    
    G --> I["generated_pdfs table"]
    I --> J["Return Success<br/>+ PDF ID"]
    
    style J fill:#90EE90
    style H fill:#FF6B6B
```

### Download Flow

```mermaid
flowchart TD
    A["Request Download"] --> B["Extract User ID from JWT"]
    B --> C["Query Database"]
    C --> D["SELECT * FROM generated_pdfs<br/>WHERE id = ?"]
    
    D --> E{"Record<br/>Found?"}
    E -->|No| F["404 Not Found"]
    E -->|Yes| G{"user_id =<br/>auth.uid()?"}
    
    G -->|No| H["403 Forbidden"]
    G -->|Yes| I["Generate Presigned URL"]
    
    I --> J["Log Download Event"]
    J --> K["Increment Counter"]
    K --> L["Stream PDF / Redirect"]
    
    style L fill:#90EE90
    style F fill:#FF6B6B
    style H fill:#FF6B6B
```

### Public Sharing Flow

```mermaid
flowchart TD
    subgraph "Enable Sharing"
        A["Owner: Toggle Public ON"]
        A --> B["UPDATE is_public = true"]
        B --> C["Return public_token"]
        C --> D["Generate Public URL"]
        D --> E["Share URL"]
    end
    
    subgraph "Public Access"
        F["Anyone: Visit Public URL"]
        F --> G["Extract public_token"]
        G --> H["Query: is_public = true<br/>AND public_token = ?"]
        H --> I{"Valid &<br/>Public?"}
        I -->|No| J["404 Not Found"]
        I -->|Yes| K["Generate Presigned URL"]
        K --> L["Log Download<br/>(user_id = NULL)"]
        L --> M["Redirect to PDF"]
    end
    
    style E fill:#90EE90
    style M fill:#90EE90
    style J fill:#FF6B6B
```

---

## Project Management Flow

### Add Project

```mermaid
flowchart TD
    A["Click 'New Project'"] --> B["Open Project Form"]
    B --> C["Enter Project Details"]
    
    subgraph "Project Data"
        D["Title"]
        E["Description"]
        F["Bullet Points"]
        G["Technologies"]
        H["Tags"]
        I["Status"]
        J["Links"]
    end
    
    C --> D & E & F & G & H & I & J
    
    D & E & F & G & H & I & J --> K["Submit"]
    K --> L["Validate Data"]
    L --> M{"Valid?"}
    
    M -->|No| N["Show Errors"]
    N --> B
    M -->|Yes| O["INSERT INTO projects"]
    O --> P["Update Project List"]
    P --> Q["Show Success Toast"]
    
    style Q fill:#90EE90
    style N fill:#FF6B6B
```

### Tag-Based Filtering

```mermaid
flowchart LR
    subgraph "Project Pool"
        P1["Project 1<br/>Tags: web, react"]
        P2["Project 2<br/>Tags: ml, python"]
        P3["Project 3<br/>Tags: web, node"]
        P4["Project 4<br/>Tags: mobile, react"]
    end
    
    subgraph "Filter"
        F["Selected Tags:<br/>react"]
    end
    
    subgraph "Result"
        R1["Project 1 ✓"]
        R4["Project 4 ✓"]
    end
    
    P1 & P2 & P3 & P4 --> F
    F --> R1 & R4
    
    style R1 fill:#90EE90
    style R4 fill:#90EE90
```

---

## AI Optimization Flow

### Content Optimization

```mermaid
flowchart TB
    A["Input Job Description"] --> B["Send to OpenRouter AI"]
    
    B --> C["Extract Keywords"]
    C --> D["Technical Skills"]
    C --> E["Soft Skills"]
    C --> F["Industry Terms"]
    C --> G["Role Requirements"]
    
    D & E & F & G --> H["Match Against Profile"]
    
    H --> I["Enhance Bullet Points"]
    I --> J["Optimize Summary"]
    J --> K["Reorder Sections"]
    K --> L["Calculate ATS Score"]
    
    L --> M{"Score >= 80?"}
    M -->|Yes| N["Ready to Generate"]
    M -->|No| O["Show Suggestions"]
    O --> P["User Makes Changes"]
    P --> H
    
    style N fill:#90EE90
```

### ATS Score Calculation

```mermaid
flowchart LR
    subgraph "Scoring Factors"
        A["Keyword Match<br/>40%"]
        B["Section Structure<br/>20%"]
        C["Bullet Quality<br/>20%"]
        D["Format Compliance<br/>20%"]
    end
    
    subgraph "Calculation"
        E["Weighted Sum"]
    end
    
    subgraph "Result"
        F["ATS Score<br/>0-100"]
    end
    
    A & B & C & D --> E
    E --> F
    
    style F fill:#ffd700
```

---

## Error Handling Flow

### Global Error Handler

```mermaid
flowchart TD
    A["API Request"] --> B{"Try<br/>Execute"}
    
    B -->|Success| C["Return Response"]
    B -->|Exception| D["Catch Error"]
    
    D --> E{"Error Type?"}
    
    E -->|Validation| F["400 Bad Request"]
    E -->|Auth| G["401 Unauthorized"]
    E -->|Permission| H["403 Forbidden"]
    E -->|Not Found| I["404 Not Found"]
    E -->|Server| J["500 Internal Error"]
    
    F & G & H & I & J --> K["Log Error"]
    K --> L["Return Error Response"]
    
    style C fill:#90EE90
    style F fill:#FFD700
    style G fill:#FF6B6B
    style H fill:#FF6B6B
    style I fill:#FFD700
    style J fill:#FF6B6B
```

---

## Security Flow

### Request Authentication

```mermaid
flowchart TD
    A["Incoming Request"] --> B["Extract Authorization Header"]
    B --> C{"Bearer Token<br/>Present?"}
    
    C -->|No| D["Check X-User-ID Header<br/>(Dev Mode)"]
    C -->|Yes| E["Verify JWT with Supabase"]
    
    D --> F{"Valid UUID?"}
    F -->|No| G["401 Unauthorized"]
    F -->|Yes| H["Set User Context"]
    
    E --> I{"Token Valid?"}
    I -->|No| G
    I -->|Yes| J["Extract user_id from JWT"]
    J --> H
    
    H --> K["Process Request"]
    K --> L["Apply RLS Policies"]
    L --> M["Return Response"]
    
    style M fill:#90EE90
    style G fill:#FF6B6B
```

---

## Deployment Flow

### CI/CD Pipeline

```mermaid
flowchart LR
    A["Push to GitHub"] --> B["GitHub Actions"]
    
    subgraph "CI"
        C["Run Tests"]
        D["Lint Code"]
        E["Type Check"]
    end
    
    subgraph "CD"
        F["Build Docker Image"]
        G["Push to Registry"]
        H["Deploy to Railway"]
    end
    
    B --> C & D & E
    C & D & E --> F
    F --> G
    G --> H
    H --> I["Production Live"]
    
    style I fill:#90EE90
```

---

## Related Documentation

- [Database Architecture](./database-architecture.md)
- [API Documentation](./api-reference.md)
- [Implementation Workflow](./implementation_workflow.md)
