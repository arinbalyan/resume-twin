"""GitHub API integration service for fetching user profile and repositories."""

import logging
from typing import Dict, Any, Optional, List
import httpx
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)


class GitHubService:
    """
    Service for interacting with GitHub's REST API.
    
    Features:
    - Fetch user profile information
    - Get user repositories (public and private with token)
    - Fetch contribution statistics
    - Get repository languages and topics
    
    API Rate Limits:
    - Unauthenticated: 60 requests/hour
    - Authenticated (token): 5000 requests/hour
    
    Get a free token at: https://github.com/settings/tokens
    - Create a "Personal Access Token (classic)"
    - Required scopes: `public_repo`, `read:user`
    """
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self):
        """Initialize GitHub service."""
        self.token = getattr(settings, 'GITHUB_TOKEN', None)
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"
            logger.info("GitHub service initialized with authentication")
        else:
            logger.warning("GitHub service initialized without token - rate limited to 60 req/hr")
    
    def is_available(self) -> bool:
        """Check if GitHub API is configured."""
        return bool(self.token)
    
    async def get_user_profile(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Fetch GitHub user profile information.
        
        Args:
            username: GitHub username
            
        Returns:
            User profile data or None if not found
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/users/{username}",
                    headers=self.headers
                )
                
                if response.status_code == 404:
                    logger.warning(f"GitHub user not found: {username}")
                    return None
                
                response.raise_for_status()
                data = response.json()
                
                return {
                    "username": data.get("login"),
                    "name": data.get("name"),
                    "email": data.get("email"),
                    "bio": data.get("bio"),
                    "company": data.get("company"),
                    "location": data.get("location"),
                    "blog": data.get("blog"),
                    "twitter_username": data.get("twitter_username"),
                    "avatar_url": data.get("avatar_url"),
                    "profile_url": data.get("html_url"),
                    "public_repos": data.get("public_repos"),
                    "public_gists": data.get("public_gists"),
                    "followers": data.get("followers"),
                    "following": data.get("following"),
                    "created_at": data.get("created_at"),
                    "hireable": data.get("hireable")
                }
                
        except httpx.HTTPStatusError as e:
            logger.error(f"GitHub API error for user {username}: {e.response.status_code}")
            return None
        except Exception as e:
            logger.error(f"Error fetching GitHub profile for {username}: {e}")
            return None
    
    async def get_user_repos(
        self, 
        username: str, 
        limit: int = 30,
        sort: str = "updated",  # stars, updated, pushed, full_name
        include_forks: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Fetch user's repositories.
        
        Args:
            username: GitHub username
            limit: Maximum number of repos to fetch (default 30, max 100)
            sort: Sort by (stars, updated, pushed, full_name)
            include_forks: Include forked repositories
            
        Returns:
            List of repository data
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/users/{username}/repos",
                    headers=self.headers,
                    params={
                        "per_page": min(limit, 100),
                        "sort": sort,
                        "direction": "desc"
                    }
                )
                
                response.raise_for_status()
                repos = response.json()
                
                # Filter and format repositories
                formatted_repos = []
                for repo in repos:
                    # Skip forks if not requested
                    if not include_forks and repo.get("fork"):
                        continue
                    
                    formatted_repos.append({
                        "name": repo.get("name"),
                        "full_name": repo.get("full_name"),
                        "description": repo.get("description"),
                        "url": repo.get("html_url"),
                        "homepage": repo.get("homepage"),
                        "language": repo.get("language"),
                        "topics": repo.get("topics", []),
                        "stars": repo.get("stargazers_count"),
                        "forks": repo.get("forks_count"),
                        "watchers": repo.get("watchers_count"),
                        "open_issues": repo.get("open_issues_count"),
                        "is_fork": repo.get("fork"),
                        "is_archived": repo.get("archived"),
                        "created_at": repo.get("created_at"),
                        "updated_at": repo.get("updated_at"),
                        "pushed_at": repo.get("pushed_at"),
                        "default_branch": repo.get("default_branch"),
                        "license": repo.get("license", {}).get("spdx_id") if repo.get("license") else None
                    })
                
                return formatted_repos[:limit]
                
        except httpx.HTTPStatusError as e:
            logger.error(f"GitHub API error fetching repos for {username}: {e.response.status_code}")
            return []
        except Exception as e:
            logger.error(f"Error fetching GitHub repos for {username}: {e}")
            return []
    
    async def get_repo_languages(self, owner: str, repo: str) -> Dict[str, int]:
        """
        Get programming languages used in a repository.
        
        Args:
            owner: Repository owner username
            repo: Repository name
            
        Returns:
            Dictionary of language -> bytes used
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/repos/{owner}/{repo}/languages",
                    headers=self.headers
                )
                
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Error fetching languages for {owner}/{repo}: {e}")
            return {}
    
    async def get_user_contribution_stats(self, username: str) -> Dict[str, Any]:
        """
        Get user's contribution statistics.
        Note: This uses the events API which has limited history.
        
        Args:
            username: GitHub username
            
        Returns:
            Contribution statistics
        """
        try:
            async with httpx.AsyncClient() as client:
                # Get recent events (limited to last 90 days, 300 events max)
                response = await client.get(
                    f"{self.BASE_URL}/users/{username}/events/public",
                    headers=self.headers,
                    params={"per_page": 100}
                )
                
                response.raise_for_status()
                events = response.json()
                
                # Count event types
                event_counts = {}
                for event in events:
                    event_type = event.get("type", "Unknown")
                    event_counts[event_type] = event_counts.get(event_type, 0) + 1
                
                return {
                    "total_recent_events": len(events),
                    "push_events": event_counts.get("PushEvent", 0),
                    "pull_request_events": event_counts.get("PullRequestEvent", 0),
                    "issue_events": event_counts.get("IssuesEvent", 0),
                    "create_events": event_counts.get("CreateEvent", 0),
                    "fork_events": event_counts.get("ForkEvent", 0),
                    "watch_events": event_counts.get("WatchEvent", 0),
                    "event_breakdown": event_counts
                }
                
        except Exception as e:
            logger.error(f"Error fetching contribution stats for {username}: {e}")
            return {}
    
    async def get_user_top_languages(self, username: str, repo_limit: int = 10) -> Dict[str, float]:
        """
        Calculate user's top programming languages from their repositories.
        
        Args:
            username: GitHub username
            repo_limit: Number of repos to analyze
            
        Returns:
            Dictionary of language -> percentage
        """
        try:
            # Get user's repositories
            repos = await self.get_user_repos(username, limit=repo_limit, sort="updated")
            
            if not repos:
                return {}
            
            # Aggregate languages from repos
            total_bytes = {}
            for repo in repos:
                languages = await self.get_repo_languages(username, repo["name"])
                for lang, bytes_count in languages.items():
                    total_bytes[lang] = total_bytes.get(lang, 0) + bytes_count
            
            # Calculate percentages
            grand_total = sum(total_bytes.values())
            if grand_total == 0:
                return {}
            
            percentages = {
                lang: round((bytes_count / grand_total) * 100, 1)
                for lang, bytes_count in sorted(
                    total_bytes.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]  # Top 10 languages
            }
            
            return percentages
            
        except Exception as e:
            logger.error(f"Error calculating top languages for {username}: {e}")
            return {}
    
    async def get_complete_profile(self, username: str) -> Dict[str, Any]:
        """
        Get complete GitHub profile including repos and stats.
        
        Args:
            username: GitHub username
            
        Returns:
            Complete profile data
        """
        try:
            # Fetch all data concurrently
            import asyncio
            
            profile_task = self.get_user_profile(username)
            repos_task = self.get_user_repos(username, limit=10, sort="stars")
            stats_task = self.get_user_contribution_stats(username)
            
            profile, repos, stats = await asyncio.gather(
                profile_task, repos_task, stats_task
            )
            
            if not profile:
                return {"error": f"User {username} not found"}
            
            # Get top languages
            languages = await self.get_user_top_languages(username, repo_limit=10)
            
            return {
                "profile": profile,
                "top_repos": repos,
                "contribution_stats": stats,
                "top_languages": languages,
                "fetched_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching complete profile for {username}: {e}")
            return {"error": str(e)}
    
    def repos_to_projects(self, repos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert GitHub repositories to resume project format.
        
        Args:
            repos: List of repository data from GitHub
            
        Returns:
            List of projects formatted for resume templates
        """
        projects = []
        
        for repo in repos:
            # Skip if no description
            if not repo.get("description"):
                continue
            
            # Create project from repo
            project = {
                "title": repo["name"].replace("-", " ").replace("_", " ").title(),
                "description": repo["description"],
                "bullet_points": [],
                "technologies": [],
                "github_url": repo["url"],
                "live_url": repo.get("homepage"),
                "start_date": None,
                "end_date": None,
                "tags": repo.get("topics", [])
            }
            
            # Add primary language to technologies
            if repo.get("language"):
                project["technologies"].append(repo["language"])
            
            # Add topics as technologies (if not too many)
            for topic in repo.get("topics", [])[:5]:
                if topic not in project["technologies"]:
                    project["technologies"].append(topic)
            
            # Generate bullet points from stats
            bullets = []
            if repo.get("stars", 0) > 0:
                bullets.append(f"Gained {repo['stars']} GitHub stars")
            if repo.get("forks", 0) > 0:
                bullets.append(f"Forked {repo['forks']} times by the community")
            if repo.get("description"):
                bullets.append(repo["description"])
            
            project["bullet_points"] = bullets[:3]
            
            # Parse dates
            if repo.get("created_at"):
                try:
                    created = datetime.fromisoformat(repo["created_at"].replace("Z", "+00:00"))
                    project["start_date"] = created.strftime("%b %Y")
                except:
                    pass
            
            projects.append(project)
        
        return projects


# Global instance
github_service = GitHubService()
