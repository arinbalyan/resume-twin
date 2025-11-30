-- Resume Twin Platform Database Schema
-- PostgreSQL Schema for Supabase Integration

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "fuzzystrmatch";

-- ============================================================================
-- USER PROFILE TABLES
-- ============================================================================

-- Profiles table (extends Supabase auth.users)
CREATE TABLE profiles (
    id UUID REFERENCES auth.users PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    phone TEXT,
    city TEXT,
    country TEXT,
    linkedin_url TEXT,
    github_url TEXT,
    portfolio_url TEXT,
    other_links JSONB DEFAULT '{}',
    avatar_url TEXT,
    bio TEXT,
    current_title TEXT,
    experience_years INTEGER DEFAULT 0,
    preferred_job_types JSONB DEFAULT '[]',
    target_industries JSONB DEFAULT '[]',
    salary_expectation_min INTEGER,
    salary_expectation_max INTEGER,
    willing_to_relocate BOOLEAN DEFAULT FALSE,
    profile_completion_score INTEGER DEFAULT 0,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Education table
CREATE TABLE education (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    institution TEXT NOT NULL,
    degree TEXT NOT NULL,
    field_of_study TEXT,
    cgpa DECIMAL(3,2),
    percentage DECIMAL(5,2),
    graduation_year INTEGER,
    location TEXT,
    start_date DATE,
    end_date DATE,
    description TEXT,
    is_current BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- PROJECT MANAGEMENT TABLES
-- ============================================================================

-- Projects table
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    short_description TEXT,
    bullet_points JSONB DEFAULT '[]',
    category TEXT NOT NULL,
    tags JSONB DEFAULT '[]',
    technologies JSONB DEFAULT '[]',
    github_url TEXT,
    live_url TEXT,
    demo_url TEXT,
    start_date DATE,
    end_date DATE,
    status TEXT DEFAULT 'completed',
    is_featured BOOLEAN DEFAULT FALSE,
    is_public BOOLEAN DEFAULT FALSE,
    difficulty_level INTEGER CHECK (difficulty_level BETWEEN 1 AND 5),
    team_size INTEGER DEFAULT 1,
    client_info TEXT,
    budget_range TEXT,
    impact_metrics JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Project media (screenshots, etc.)
CREATE TABLE project_media (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    file_url TEXT NOT NULL,
    file_name TEXT,
    file_size BIGINT,
    media_type TEXT,
    caption TEXT,
    alt_text TEXT,
    display_order INTEGER DEFAULT 0,
    is_cover_image BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Project technologies
CREATE TABLE project_technologies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    technology_name TEXT NOT NULL,
    technology_category TEXT,
    proficiency_level INTEGER CHECK (proficiency_level BETWEEN 1 AND 5),
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- PROFESSIONAL EXPERIENCE TABLES
-- ============================================================================

-- Professional certifications
CREATE TABLE certifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    issuer TEXT NOT NULL,
    issue_date DATE,
    expiry_date DATE,
    credential_id TEXT,
    verification_url TEXT,
    certificate_file_url TEXT,
    skills_acquired JSONB DEFAULT '[]',
    description TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Internship experiences
CREATE TABLE internships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    company TEXT NOT NULL,
    role TEXT NOT NULL,
    location TEXT,
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT FALSE,
    description TEXT,
    achievements JSONB DEFAULT '[]',
    key_learnings JSONB DEFAULT '[]',
    team_size INTEGER,
    project_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Courses completed
CREATE TABLE courses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    institution TEXT,
    instructor TEXT,
    completion_date DATE,
    certificate_url TEXT,
    course_url TEXT,
    skills_acquired JSONB DEFAULT '[]',
    description TEXT,
    duration_hours INTEGER,
    difficulty_level INTEGER CHECK (difficulty_level BETWEEN 1 AND 5),
    is_featured BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Extracurricular activities
CREATE TABLE activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    organization TEXT,
    role TEXT,
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT FALSE,
    description TEXT,
    achievements JSONB DEFAULT '[]',
    activity_type TEXT,
    impact_scope TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- RESUME GENERATION TABLES
-- ============================================================================

-- LaTeX templates
CREATE TABLE templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    subcategory TEXT,
    description TEXT,
    latex_content TEXT NOT NULL,
    css_styles TEXT,
    preview_image_url TEXT,
    thumbnail_url TEXT,
    is_public BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    download_count INTEGER DEFAULT 0,
    rating DECIMAL(3,2) DEFAULT 0,
    rating_count INTEGER DEFAULT 0,
    created_by UUID REFERENCES profiles(id),
    tags JSONB DEFAULT '[]',
    compatibility JSONB DEFAULT '{}',
    customization_options JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Template ratings and reviews
CREATE TABLE template_ratings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID REFERENCES templates(id) ON DELETE CASCADE,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    review TEXT,
    is_featured_review BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(template_id, user_id)
);

-- User resume versions
CREATE TABLE resume_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    template_id UUID REFERENCES templates(id),
    title TEXT NOT NULL,
    job_description TEXT,
    selected_project_ids JSONB DEFAULT '[]',
    selected_tags JSONB DEFAULT '[]',
    optimized_content JSONB,
    latex_content TEXT,
    pdf_url TEXT,
    preview_url TEXT,
    is_ai_optimized BOOLEAN DEFAULT FALSE,
    optimization_score INTEGER,
    optimization_version INTEGER DEFAULT 1,
    sections_included JSONB DEFAULT '[]',
    customizations JSONB DEFAULT '{}',
    status TEXT DEFAULT 'draft',
    is_default BOOLEAN DEFAULT FALSE,
    is_public BOOLEAN DEFAULT FALSE,
    download_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI optimization history
CREATE TABLE optimization_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resume_version_id UUID REFERENCES resume_versions(id) ON DELETE CASCADE,
    job_description TEXT NOT NULL,
    keywords_extracted JSONB,
    optimization_applied JSONB,
    before_score INTEGER,
    after_score INTEGER,
    optimization_type TEXT,
    ai_model_version TEXT,
    processing_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- FILE MANAGEMENT TABLES
-- ============================================================================

-- File uploads
CREATE TABLE file_uploads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    original_filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size BIGINT,
    mime_type TEXT,
    file_category TEXT,
    upload_status TEXT DEFAULT 'pending',
    virus_scan_status TEXT DEFAULT 'pending',
    processing_status TEXT DEFAULT 'pending',
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Profile indexes
CREATE INDEX idx_profiles_email ON profiles(email);
CREATE INDEX idx_profiles_city ON profiles(city);
CREATE INDEX idx_profiles_country ON profiles(country);
CREATE INDEX idx_profiles_current_title ON profiles(current_title);
CREATE INDEX idx_profiles_experience_years ON profiles(experience_years);

-- Education indexes
CREATE INDEX idx_education_user_id ON education(user_id);
CREATE INDEX idx_education_graduation_year ON education(graduation_year);
CREATE INDEX idx_education_institution ON education(institution);

-- Project indexes
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_projects_category ON projects(category);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_is_featured ON projects(is_featured);
CREATE INDEX idx_projects_created_at ON projects(created_at);
CREATE INDEX idx_projects_tags ON projects USING gin(tags);
CREATE INDEX idx_projects_search ON projects USING gin(to_tsvector('english', title || ' ' || COALESCE(description, '')));

-- Project media indexes
CREATE INDEX idx_project_media_project_id ON project_media(project_id);
CREATE INDEX idx_project_media_display_order ON project_media(display_order);

-- Professional experience indexes
CREATE INDEX idx_certifications_user_id ON certifications(user_id);
CREATE INDEX idx_certifications_issuer ON certifications(issuer);
CREATE INDEX idx_internships_user_id ON internships(user_id);
CREATE INDEX idx_internships_company ON internships(company);
CREATE INDEX idx_courses_user_id ON courses(user_id);
CREATE INDEX idx_courses_institution ON courses(institution);
CREATE INDEX idx_activities_user_id ON activities(user_id);
CREATE INDEX idx_activities_organization ON activities(organization);

-- Resume and template indexes
CREATE INDEX idx_templates_category ON templates(category);
CREATE INDEX idx_templates_is_public ON templates(is_public);
CREATE INDEX idx_templates_is_featured ON templates(is_featured);
CREATE INDEX idx_templates_created_at ON templates(created_at);
CREATE INDEX idx_template_ratings_template_id ON template_ratings(template_id);

CREATE INDEX idx_resume_versions_user_id ON resume_versions(user_id);
CREATE INDEX idx_resume_versions_template_id ON resume_versions(template_id);
CREATE INDEX idx_resume_versions_status ON resume_versions(status);
CREATE INDEX idx_resume_versions_created_at ON resume_versions(created_at);

-- File upload indexes
CREATE INDEX idx_file_uploads_user_id ON file_uploads(user_id);
CREATE INDEX idx_file_uploads_file_category ON file_uploads(file_category);
CREATE INDEX idx_file_uploads_upload_status ON file_uploads(upload_status);
CREATE INDEX idx_file_uploads_expires_at ON file_uploads(expires_at);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS on all user tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE education ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_media ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_technologies ENABLE ROW LEVEL SECURITY;
ALTER TABLE certifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE internships ENABLE ROW LEVEL SECURITY;
ALTER TABLE courses ENABLE ROW LEVEL SECURITY;
ALTER TABLE activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE resume_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE optimization_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE file_uploads ENABLE ROW LEVEL SECURITY;

-- Public templates are readable by everyone
ALTER TABLE templates ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public templates are viewable by everyone" ON templates FOR SELECT USING (is_public = true);
CREATE POLICY "Users can view their own templates" ON templates FOR ALL USING (auth.uid() = created_by);

-- Template ratings policies
ALTER TABLE template_ratings ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view all template ratings" ON template_ratings FOR SELECT USING (true);
CREATE POLICY "Users can manage their own ratings" ON template_ratings FOR ALL USING (auth.uid() = user_id);

-- Profile policies
CREATE POLICY "Users can view public profiles" ON profiles FOR SELECT USING (is_public = true OR auth.uid() = id);
CREATE POLICY "Users can update own profile" ON profiles FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Users can insert own profile" ON profiles FOR INSERT WITH CHECK (auth.uid() = id);

-- Education policies
CREATE POLICY "Users can manage own education" ON education FOR ALL USING (auth.uid() = user_id);

-- Project policies
CREATE POLICY "Users can view public projects" ON projects FOR SELECT USING (is_public = true OR auth.uid() = user_id);
CREATE POLICY "Users can manage own projects" ON projects FOR ALL USING (auth.uid() = user_id);

-- Project media policies
CREATE POLICY "Users can manage media for own projects" ON project_media FOR ALL USING (
    EXISTS (SELECT 1 FROM projects WHERE projects.id = project_media.project_id AND projects.user_id = auth.uid())
);

-- Professional experience policies
CREATE POLICY "Users can manage own certifications" ON certifications FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own internships" ON internships FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own courses" ON courses FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own activities" ON activities FOR ALL USING (auth.uid() = user_id);

-- Resume policies
CREATE POLICY "Users can view public resume versions" ON resume_versions FOR SELECT USING (is_public = true OR auth.uid() = user_id);
CREATE POLICY "Users can manage own resume versions" ON resume_versions FOR ALL USING (auth.uid() = user_id);

-- Optimization history policies
CREATE POLICY "Users can view own optimization history" ON optimization_history FOR SELECT USING (
    EXISTS (SELECT 1 FROM resume_versions WHERE resume_versions.id = optimization_history.resume_version_id AND resume_versions.user_id = auth.uid())
);
CREATE POLICY "Users can insert own optimization history" ON optimization_history FOR INSERT WITH CHECK (
    EXISTS (SELECT 1 FROM resume_versions WHERE resume_versions.id = optimization_history.resume_version_id AND resume_versions.user_id = auth.uid())
);

-- File upload policies
CREATE POLICY "Users can manage own file uploads" ON file_uploads FOR ALL USING (auth.uid() = user_id);

-- ============================================================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- ============================================================================

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers to relevant tables
CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_education_updated_at BEFORE UPDATE ON education
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_certifications_updated_at BEFORE UPDATE ON certifications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_internships_updated_at BEFORE UPDATE ON internships
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_courses_updated_at BEFORE UPDATE ON courses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_activities_updated_at BEFORE UPDATE ON activities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_templates_updated_at BEFORE UPDATE ON templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_resume_versions_updated_at BEFORE UPDATE ON resume_versions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- User profile completion view
CREATE VIEW profile_completion AS
SELECT 
    p.id,
    p.full_name,
    p.email,
    p.current_title,
    p.bio,
    p.avatar_url,
    p.linkedin_url,
    p.github_url,
    p.portfolio_url,
    -- Education completion
    CASE WHEN EXISTS (SELECT 1 FROM education e WHERE e.user_id = p.id) THEN 1 ELSE 0 END as has_education,
    -- Projects completion
    CASE WHEN EXISTS (SELECT 1 FROM projects pr WHERE pr.user_id = p.id) THEN 1 ELSE 0 END as has_projects,
    -- Experience completion
    CASE WHEN EXISTS (SELECT 1 FROM certifications c WHERE c.user_id = p.id) 
         OR EXISTS (SELECT 1 FROM internships i WHERE i.user_id = p.id) 
         OR EXISTS (SELECT 1 FROM activities a WHERE a.user_id = p.id) 
         THEN 1 ELSE 0 END as has_experience,
    -- Skills completion
    CASE WHEN EXISTS (SELECT 1 FROM project_technologies pt 
                     JOIN projects pr ON pr.id = pt.project_id 
                     WHERE pr.user_id = p.id) THEN 1 ELSE 0 END as has_skills,
    -- Resume completion
    CASE WHEN EXISTS (SELECT 1 FROM resume_versions rv WHERE rv.user_id = p.id) THEN 1 ELSE 0 END as has_resume,
    COUNT(pr.id) as project_count,
    COUNT(DISTINCT pr.category) as project_categories,
    COUNT(DISTINCT pt.technology_name) as unique_technologies
FROM profiles p
LEFT JOIN projects pr ON pr.user_id = p.id
LEFT JOIN project_technologies pt ON pt.project_id = pr.id
GROUP BY p.id, p.full_name, p.email, p.current_title, p.bio, p.avatar_url, p.linkedin_url, p.github_url, p.portfolio_url;

-- Template statistics view
CREATE VIEW template_stats AS
SELECT 
    t.id,
    t.name,
    t.category,
    t.is_featured,
    t.download_count,
    t.rating,
    t.rating_count,
    COUNT(rv.id) as usage_count,
    AVG(rv.optimization_score) as avg_optimization_score
FROM templates t
LEFT JOIN resume_versions rv ON rv.template_id = t.id
GROUP BY t.id, t.name, t.category, t.is_featured, t.download_count, t.rating, t.rating_count;