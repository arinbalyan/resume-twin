"""Resume scoring and ATS (Applicant Tracking System) analysis service."""

import logging
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from collections import Counter

logger = logging.getLogger(__name__)


@dataclass
class ScoringResult:
    """Result of resume scoring."""
    overall_score: int  # 0-100
    category_scores: Dict[str, int]
    issues: List[Dict[str, str]]
    suggestions: List[str]
    keyword_matches: Dict[str, int]
    ats_compatibility: int  # 0-100


class ResumeScorer:
    """
    Resume scoring and ATS analysis service.
    
    Features:
    - Overall resume quality score
    - Section-by-section scoring
    - ATS keyword matching
    - Actionable suggestions
    - Job description matching (optional)
    
    No API key required - runs locally!
    """
    
    # Keywords that ATS systems commonly look for
    ACTION_VERBS = {
        "achieved", "administered", "advanced", "analyzed", "built", "collaborated",
        "conducted", "created", "decreased", "delivered", "designed", "developed",
        "directed", "enhanced", "established", "exceeded", "executed", "generated",
        "improved", "increased", "initiated", "implemented", "launched", "led",
        "managed", "negotiated", "optimized", "organized", "performed", "planned",
        "produced", "reduced", "resolved", "restructured", "spearheaded", "streamlined",
        "supervised", "trained", "transformed", "upgraded"
    }
    
    # Common technical skills categories
    TECH_SKILLS = {
        "languages": ["python", "javascript", "typescript", "java", "c++", "c#", "go", 
                     "rust", "ruby", "php", "swift", "kotlin", "scala", "r"],
        "frameworks": ["react", "angular", "vue", "django", "flask", "fastapi", "express",
                      "nextjs", "spring", "laravel", ".net", "rails"],
        "databases": ["postgresql", "mysql", "mongodb", "redis", "elasticsearch", 
                     "cassandra", "dynamodb", "sqlite", "oracle", "sql server"],
        "cloud": ["aws", "gcp", "azure", "heroku", "vercel", "netlify", "digitalocean"],
        "devops": ["docker", "kubernetes", "jenkins", "terraform", "ansible", "github actions",
                  "gitlab ci", "circleci", "prometheus", "grafana"]
    }
    
    # Minimum recommended content lengths
    MIN_SUMMARY_LENGTH = 150
    MIN_EXPERIENCE_BULLETS = 3
    MIN_SKILLS = 5
    MIN_PROJECTS = 2
    
    def __init__(self):
        """Initialize the resume scorer."""
        logger.info("Resume scorer initialized")
    
    def score_resume(
        self, 
        resume_data: Dict[str, Any],
        job_description: Optional[str] = None
    ) -> ScoringResult:
        """
        Score a resume and provide feedback.
        
        Args:
            resume_data: Resume data dictionary with sections
            job_description: Optional job description for keyword matching
            
        Returns:
            ScoringResult with scores and suggestions
        """
        issues = []
        suggestions = []
        category_scores = {}
        keyword_matches = {}
        
        # Score each section
        category_scores["contact"] = self._score_contact(resume_data, issues, suggestions)
        category_scores["summary"] = self._score_summary(resume_data, issues, suggestions)
        category_scores["experience"] = self._score_experience(resume_data, issues, suggestions)
        category_scores["skills"] = self._score_skills(resume_data, issues, suggestions)
        category_scores["projects"] = self._score_projects(resume_data, issues, suggestions)
        category_scores["education"] = self._score_education(resume_data, issues, suggestions)
        
        # Calculate overall score (weighted average)
        weights = {
            "contact": 0.10,
            "summary": 0.15,
            "experience": 0.30,
            "skills": 0.15,
            "projects": 0.20,
            "education": 0.10
        }
        
        overall_score = sum(
            category_scores.get(cat, 0) * weight 
            for cat, weight in weights.items()
        )
        
        # Score ATS compatibility
        ats_score = self._score_ats_compatibility(resume_data, issues, suggestions)
        
        # Match against job description if provided
        if job_description:
            keyword_matches = self._match_job_keywords(resume_data, job_description)
            jd_match_score = self._calculate_jd_match_score(keyword_matches)
            # Blend with overall score
            overall_score = (overall_score * 0.7) + (jd_match_score * 0.3)
        
        return ScoringResult(
            overall_score=round(overall_score),
            category_scores=category_scores,
            issues=issues,
            suggestions=suggestions,
            keyword_matches=keyword_matches,
            ats_compatibility=ats_score
        )
    
    def _score_contact(
        self, 
        data: Dict[str, Any], 
        issues: List[Dict], 
        suggestions: List[str]
    ) -> int:
        """Score contact information section."""
        score = 0
        max_score = 100
        
        # Check required fields
        if data.get("user_name"):
            score += 30
        else:
            issues.append({
                "section": "contact",
                "severity": "error",
                "message": "Missing name"
            })
        
        if data.get("email"):
            score += 25
            # Validate email format
            if not re.match(r"[^@]+@[^@]+\.[^@]+", data["email"]):
                issues.append({
                    "section": "contact",
                    "severity": "warning",
                    "message": "Email format may be invalid"
                })
                score -= 10
        else:
            issues.append({
                "section": "contact",
                "severity": "error",
                "message": "Missing email address"
            })
        
        if data.get("phone"):
            score += 15
        
        if data.get("linkedin"):
            score += 15
        else:
            suggestions.append("Add your LinkedIn profile URL for better networking")
        
        if data.get("github"):
            score += 10
            
        if data.get("location"):
            score += 5
        
        return min(score, max_score)
    
    def _score_summary(
        self, 
        data: Dict[str, Any], 
        issues: List[Dict], 
        suggestions: List[str]
    ) -> int:
        """Score professional summary section."""
        summary = data.get("summary", "")
        
        if not summary:
            issues.append({
                "section": "summary",
                "severity": "warning",
                "message": "No professional summary provided"
            })
            return 0
        
        score = 50  # Base score for having a summary
        
        # Check length
        word_count = len(summary.split())
        if word_count < 30:
            issues.append({
                "section": "summary",
                "severity": "warning",
                "message": f"Summary is too short ({word_count} words). Aim for 50-150 words."
            })
        elif word_count > 200:
            issues.append({
                "section": "summary",
                "severity": "info",
                "message": "Summary might be too long. Consider condensing to key points."
            })
        else:
            score += 20
        
        # Check for action verbs
        summary_lower = summary.lower()
        action_count = sum(1 for verb in self.ACTION_VERBS if verb in summary_lower)
        if action_count >= 3:
            score += 15
        elif action_count >= 1:
            score += 8
        else:
            suggestions.append("Use action verbs in your summary (e.g., 'led', 'developed', 'achieved')")
        
        # Check for quantifiable achievements
        if re.search(r'\d+%|\d+\+|\d+ years?|\$\d+', summary):
            score += 15
        else:
            suggestions.append("Add quantifiable achievements to your summary (e.g., '10+ years', '50% improvement')")
        
        return min(score, 100)
    
    def _score_experience(
        self, 
        data: Dict[str, Any], 
        issues: List[Dict], 
        suggestions: List[str]
    ) -> int:
        """Score work experience section."""
        experience = data.get("experience", [])
        
        if not experience:
            issues.append({
                "section": "experience",
                "severity": "warning",
                "message": "No work experience listed"
            })
            return 0
        
        score = 40  # Base score for having experience
        
        # Check number of positions
        if len(experience) >= 3:
            score += 15
        elif len(experience) >= 2:
            score += 10
        
        total_bullets = 0
        action_verb_bullets = 0
        quantified_bullets = 0
        
        for exp in experience:
            achievements = exp.get("achievements", [])
            total_bullets += len(achievements)
            
            for achievement in achievements:
                # Check for action verbs at start
                first_word = achievement.split()[0].lower() if achievement else ""
                if first_word in self.ACTION_VERBS or first_word.rstrip("ed") in self.ACTION_VERBS:
                    action_verb_bullets += 1
                
                # Check for numbers/metrics
                if re.search(r'\d+%?|\$\d+', achievement):
                    quantified_bullets += 1
        
        # Score bullet points
        if total_bullets >= len(experience) * 3:
            score += 15
        elif total_bullets >= len(experience) * 2:
            score += 10
        else:
            suggestions.append("Add at least 3-5 bullet points per job position")
        
        # Score action verbs usage
        if total_bullets > 0:
            action_ratio = action_verb_bullets / total_bullets
            if action_ratio >= 0.7:
                score += 15
            elif action_ratio >= 0.5:
                score += 10
            else:
                suggestions.append("Start each achievement with a strong action verb")
        
        # Score quantification
        if total_bullets > 0:
            quant_ratio = quantified_bullets / total_bullets
            if quant_ratio >= 0.5:
                score += 15
            elif quant_ratio >= 0.3:
                score += 10
            else:
                suggestions.append("Add metrics and numbers to your achievements (%, $, time saved)")
        
        return min(score, 100)
    
    def _score_skills(
        self, 
        data: Dict[str, Any], 
        issues: List[Dict], 
        suggestions: List[str]
    ) -> int:
        """Score skills section."""
        skills = data.get("skills", {})
        
        if not skills:
            issues.append({
                "section": "skills",
                "severity": "warning",
                "message": "No skills listed"
            })
            return 0
        
        score = 40  # Base score for having skills
        
        # Count total skills
        total_skills = 0
        if isinstance(skills, dict):
            for category_skills in skills.values():
                if isinstance(category_skills, list):
                    total_skills += len(category_skills)
        elif isinstance(skills, list):
            total_skills = len(skills)
        
        if total_skills >= 15:
            score += 25
        elif total_skills >= 10:
            score += 20
        elif total_skills >= 5:
            score += 15
        else:
            suggestions.append("Add more skills (aim for 10-15 relevant skills)")
        
        # Check for skill categorization
        if isinstance(skills, dict) and len(skills) >= 3:
            score += 15
        else:
            suggestions.append("Organize skills into categories (e.g., Languages, Frameworks, Tools)")
        
        # Check for technical skills
        all_skills_str = str(skills).lower()
        tech_skill_count = 0
        for category, tech_list in self.TECH_SKILLS.items():
            for skill in tech_list:
                if skill in all_skills_str:
                    tech_skill_count += 1
        
        if tech_skill_count >= 10:
            score += 20
        elif tech_skill_count >= 5:
            score += 15
        
        return min(score, 100)
    
    def _score_projects(
        self, 
        data: Dict[str, Any], 
        issues: List[Dict], 
        suggestions: List[str]
    ) -> int:
        """Score projects section."""
        projects = data.get("projects", [])
        
        if not projects:
            suggestions.append("Consider adding personal or professional projects to showcase your skills")
            return 30  # Base score even without projects
        
        score = 50  # Base score for having projects
        
        if len(projects) >= 4:
            score += 15
        elif len(projects) >= 2:
            score += 10
        
        has_descriptions = sum(1 for p in projects if p.get("description"))
        has_technologies = sum(1 for p in projects if p.get("technologies"))
        has_links = sum(1 for p in projects if p.get("github_url") or p.get("live_url"))
        has_bullets = sum(1 for p in projects if p.get("bullet_points"))
        
        # Score completeness
        if has_descriptions == len(projects):
            score += 10
        else:
            suggestions.append("Add descriptions to all projects")
        
        if has_technologies == len(projects):
            score += 10
        else:
            suggestions.append("List technologies used for each project")
        
        if has_links >= len(projects) * 0.5:
            score += 10
        else:
            suggestions.append("Add GitHub or demo links to your projects")
        
        if has_bullets >= len(projects) * 0.5:
            score += 5
        
        return min(score, 100)
    
    def _score_education(
        self, 
        data: Dict[str, Any], 
        issues: List[Dict], 
        suggestions: List[str]
    ) -> int:
        """Score education section."""
        education = data.get("education", [])
        certifications = data.get("certifications", [])
        
        score = 0
        
        if education:
            score += 50
            
            for edu in education:
                if edu.get("degree"):
                    score += 15
                if edu.get("institution"):
                    score += 10
                if edu.get("gpa") and float(edu.get("gpa", 0)) >= 3.5:
                    score += 10
        else:
            issues.append({
                "section": "education",
                "severity": "info",
                "message": "No education listed"
            })
        
        # Bonus for certifications
        if certifications:
            score += min(len(certifications) * 5, 15)
        else:
            suggestions.append("Consider adding relevant certifications to strengthen your profile")
        
        return min(score, 100)
    
    def _score_ats_compatibility(
        self, 
        data: Dict[str, Any], 
        issues: List[Dict], 
        suggestions: List[str]
    ) -> int:
        """Score ATS (Applicant Tracking System) compatibility."""
        score = 70  # Base score
        
        # Check for common ATS issues
        
        # 1. Plain text compatibility (already covered by using templates)
        score += 10
        
        # 2. Standard section names
        has_standard_sections = all([
            data.get("summary") or data.get("objective"),
            data.get("experience"),
            data.get("education"),
            data.get("skills")
        ])
        if has_standard_sections:
            score += 10
        else:
            suggestions.append("Use standard section names (Summary, Experience, Education, Skills)")
        
        # 3. No special characters in important fields
        name = data.get("user_name", "")
        if not re.search(r'[^\w\s\-\.]', name):
            score += 5
        else:
            issues.append({
                "section": "ats",
                "severity": "warning",
                "message": "Avoid special characters in your name for ATS compatibility"
            })
        
        # 4. Date formatting consistency
        score += 5  # Assume good formatting from templates
        
        return min(score, 100)
    
    def _match_job_keywords(
        self, 
        resume_data: Dict[str, Any], 
        job_description: str
    ) -> Dict[str, int]:
        """Match resume against job description keywords."""
        # Extract keywords from job description
        jd_words = set(re.findall(r'\b[a-zA-Z+#]{3,}\b', job_description.lower()))
        
        # Get all resume text
        resume_text = self._get_all_text(resume_data).lower()
        
        # Find matches
        matches = {}
        for word in jd_words:
            count = len(re.findall(r'\b' + re.escape(word) + r'\b', resume_text))
            if count > 0:
                matches[word] = count
        
        return dict(sorted(matches.items(), key=lambda x: x[1], reverse=True)[:20])
    
    def _calculate_jd_match_score(self, keyword_matches: Dict[str, int]) -> int:
        """Calculate score based on keyword matches."""
        if not keyword_matches:
            return 50
        
        total_matches = sum(keyword_matches.values())
        unique_matches = len(keyword_matches)
        
        # Score based on coverage
        if unique_matches >= 15:
            return 95
        elif unique_matches >= 10:
            return 85
        elif unique_matches >= 5:
            return 70
        else:
            return 50
    
    def _get_all_text(self, data: Dict[str, Any]) -> str:
        """Extract all text from resume data."""
        texts = []
        
        # Add string fields
        for key in ["user_name", "title", "summary", "email"]:
            if data.get(key):
                texts.append(str(data[key]))
        
        # Add skills
        skills = data.get("skills", {})
        if isinstance(skills, dict):
            for skill_list in skills.values():
                texts.extend(str(s) for s in skill_list)
        elif isinstance(skills, list):
            texts.extend(str(s) for s in skills)
        
        # Add experience
        for exp in data.get("experience", []):
            texts.append(exp.get("position", ""))
            texts.append(exp.get("company", ""))
            for achievement in exp.get("achievements", []):
                texts.append(achievement)
        
        # Add projects
        for proj in data.get("projects", []):
            texts.append(proj.get("title", ""))
            texts.append(proj.get("description", ""))
            texts.extend(proj.get("technologies", []))
            texts.extend(proj.get("bullet_points", []))
        
        return " ".join(texts)
    
    def get_improvement_priority(self, result: ScoringResult) -> List[Dict[str, str]]:
        """Get prioritized list of improvements."""
        priorities = []
        
        # Sort categories by score (lowest first)
        sorted_categories = sorted(
            result.category_scores.items(),
            key=lambda x: x[1]
        )
        
        for category, score in sorted_categories:
            if score < 70:
                priorities.append({
                    "category": category,
                    "current_score": score,
                    "priority": "high" if score < 50 else "medium",
                    "impact": "This section significantly affects your overall score"
                })
        
        return priorities


# Global instance
resume_scorer = ResumeScorer()
