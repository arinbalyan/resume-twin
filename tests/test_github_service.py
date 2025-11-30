"""
Unit Tests for GitHub Service.

Tests cover:
- User profile fetching
- Repository listing and filtering
- Language statistics calculation
- Contribution stats
- Complete profile aggregation
- Repository to project conversion
- Error handling and rate limiting
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime
import json
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


# ============================================================================
# GitHub Service Initialization Tests
# ============================================================================

class TestGitHubServiceInit:
    """Tests for GitHub service initialization."""
    
    def test_init_with_token(self):
        """Should initialize with authentication when token is provided."""
        with patch('app.services.github_service.settings') as mock_settings:
            mock_settings.GITHUB_TOKEN = "test-token"
            
            from app.services.github_service import GitHubService
            service = GitHubService()
            
            assert service.token == "test-token"
            assert "Authorization" in service.headers
            assert service.headers["Authorization"] == "Bearer test-token"
    
    def test_init_without_token(self):
        """Should initialize without authentication when no token."""
        with patch('app.services.github_service.settings') as mock_settings:
            mock_settings.GITHUB_TOKEN = None
            
            from app.services.github_service import GitHubService
            service = GitHubService()
            
            assert service.token is None
            assert "Authorization" not in service.headers
    
    def test_is_available_with_token(self):
        """Should return True when token is configured."""
        with patch('app.services.github_service.settings') as mock_settings:
            mock_settings.GITHUB_TOKEN = "test-token"
            
            from app.services.github_service import GitHubService
            service = GitHubService()
            
            assert service.is_available() is True
    
    def test_is_available_without_token(self):
        """Should return False when no token."""
        with patch('app.services.github_service.settings') as mock_settings:
            mock_settings.GITHUB_TOKEN = None
            
            from app.services.github_service import GitHubService
            service = GitHubService()
            
            assert service.is_available() is False


# ============================================================================
# User Profile Tests
# ============================================================================

class TestGetUserProfile:
    """Tests for fetching user profiles."""
    
    @pytest.fixture
    def github_service(self):
        """Create GitHub service instance."""
        with patch('app.services.github_service.settings') as mock_settings:
            mock_settings.GITHUB_TOKEN = "test-token"
            from app.services.github_service import GitHubService
            return GitHubService()
    
    @pytest.mark.asyncio
    async def test_get_user_profile_success(self, github_service, sample_github_profile):
        """Should successfully fetch user profile."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "login": sample_github_profile["username"],
            "name": sample_github_profile["name"],
            "email": sample_github_profile["email"],
            "bio": sample_github_profile["bio"],
            "company": sample_github_profile["company"],
            "location": sample_github_profile["location"],
            "blog": sample_github_profile["blog"],
            "twitter_username": sample_github_profile["twitter_username"],
            "avatar_url": sample_github_profile["avatar_url"],
            "html_url": sample_github_profile["profile_url"],
            "public_repos": sample_github_profile["public_repos"],
            "public_gists": sample_github_profile["public_gists"],
            "followers": sample_github_profile["followers"],
            "following": sample_github_profile["following"],
            "created_at": sample_github_profile["created_at"],
            "hireable": sample_github_profile["hireable"]
        }
        mock_response.raise_for_status = MagicMock()
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            result = await github_service.get_user_profile("johndoe")
            
            assert result is not None
            assert result["username"] == "johndoe"
            assert result["name"] == "John Doe"
            assert result["public_repos"] == 50
    
    @pytest.mark.asyncio
    async def test_get_user_profile_not_found(self, github_service):
        """Should return None when user not found."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            result = await github_service.get_user_profile("nonexistent_user")
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_get_user_profile_api_error(self, github_service):
        """Should handle API errors gracefully."""
        import httpx
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=httpx.HTTPStatusError("Error", request=MagicMock(), response=MagicMock(status_code=500))
            )
            
            result = await github_service.get_user_profile("johndoe")
            
            assert result is None


# ============================================================================
# Repository Tests
# ============================================================================

class TestGetUserRepos:
    """Tests for fetching user repositories."""
    
    @pytest.fixture
    def github_service(self):
        """Create GitHub service instance."""
        with patch('app.services.github_service.settings') as mock_settings:
            mock_settings.GITHUB_TOKEN = "test-token"
            from app.services.github_service import GitHubService
            return GitHubService()
    
    @pytest.mark.asyncio
    async def test_get_user_repos_success(self, github_service, sample_github_repos):
        """Should successfully fetch user repositories."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "name": repo["name"],
                "full_name": repo["full_name"],
                "description": repo["description"],
                "html_url": repo["url"],
                "homepage": repo["homepage"],
                "language": repo["language"],
                "topics": repo["topics"],
                "stargazers_count": repo["stars"],
                "forks_count": repo["forks"],
                "watchers_count": repo["watchers"],
                "open_issues_count": repo["open_issues"],
                "fork": repo["is_fork"],
                "archived": repo["is_archived"],
                "created_at": repo["created_at"],
                "updated_at": repo["updated_at"],
                "pushed_at": repo["pushed_at"],
                "default_branch": repo["default_branch"],
                "license": {"spdx_id": repo["license"]} if repo["license"] else None
            }
            for repo in sample_github_repos
        ]
        mock_response.raise_for_status = MagicMock()
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            result = await github_service.get_user_repos("johndoe", limit=10)
            
            assert len(result) == 2
            assert result[0]["name"] == "awesome-project"
            assert result[0]["stars"] == 150
    
    @pytest.mark.asyncio
    async def test_get_user_repos_exclude_forks(self, github_service):
        """Should exclude forked repositories by default."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"name": "original-repo", "fork": False, "description": "Original"},
            {"name": "forked-repo", "fork": True, "description": "Forked"}
        ]
        mock_response.raise_for_status = MagicMock()
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            result = await github_service.get_user_repos("johndoe", include_forks=False)
            
            assert len(result) == 1
            assert result[0]["name"] == "original-repo"
    
    @pytest.mark.asyncio
    async def test_get_user_repos_include_forks(self, github_service):
        """Should include forked repositories when requested."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"name": "original-repo", "fork": False, "description": "Original"},
            {"name": "forked-repo", "fork": True, "description": "Forked"}
        ]
        mock_response.raise_for_status = MagicMock()
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            result = await github_service.get_user_repos("johndoe", include_forks=True)
            
            assert len(result) == 2
    
    @pytest.mark.asyncio
    async def test_get_user_repos_respects_limit(self, github_service):
        """Should respect the limit parameter."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"name": f"repo-{i}", "fork": False} for i in range(50)
        ]
        mock_response.raise_for_status = MagicMock()
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            result = await github_service.get_user_repos("johndoe", limit=5)
            
            assert len(result) == 5


# ============================================================================
# Language Statistics Tests
# ============================================================================

class TestLanguageStatistics:
    """Tests for language statistics."""
    
    @pytest.fixture
    def github_service(self):
        """Create GitHub service instance."""
        with patch('app.services.github_service.settings') as mock_settings:
            mock_settings.GITHUB_TOKEN = "test-token"
            from app.services.github_service import GitHubService
            return GitHubService()
    
    @pytest.mark.asyncio
    async def test_get_repo_languages(self, github_service):
        """Should fetch repository languages."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Python": 50000,
            "JavaScript": 30000,
            "HTML": 10000
        }
        mock_response.raise_for_status = MagicMock()
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            result = await github_service.get_repo_languages("johndoe", "awesome-project")
            
            assert result["Python"] == 50000
            assert "JavaScript" in result
    
    @pytest.mark.asyncio
    async def test_get_user_top_languages(self, github_service):
        """Should calculate top languages from user repos."""
        # Mock get_user_repos
        mock_repos = [{"name": "repo1"}, {"name": "repo2"}]
        
        # Mock language responses
        mock_languages = [
            {"Python": 50000, "JavaScript": 20000},
            {"Python": 30000, "TypeScript": 40000}
        ]
        
        with patch.object(github_service, 'get_user_repos', new_callable=AsyncMock) as mock_get_repos:
            mock_get_repos.return_value = mock_repos
            
            with patch.object(github_service, 'get_repo_languages', new_callable=AsyncMock) as mock_get_langs:
                mock_get_langs.side_effect = mock_languages
                
                result = await github_service.get_user_top_languages("johndoe", repo_limit=2)
                
                assert "Python" in result
                # Python should be highest (80000 bytes total)
                assert result["Python"] > result.get("TypeScript", 0)


# ============================================================================
# Contribution Stats Tests
# ============================================================================

class TestContributionStats:
    """Tests for contribution statistics."""
    
    @pytest.fixture
    def github_service(self):
        """Create GitHub service instance."""
        with patch('app.services.github_service.settings') as mock_settings:
            mock_settings.GITHUB_TOKEN = "test-token"
            from app.services.github_service import GitHubService
            return GitHubService()
    
    @pytest.mark.asyncio
    async def test_get_contribution_stats(self, github_service):
        """Should fetch and calculate contribution stats."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"type": "PushEvent"},
            {"type": "PushEvent"},
            {"type": "PullRequestEvent"},
            {"type": "IssuesEvent"},
            {"type": "CreateEvent"}
        ]
        mock_response.raise_for_status = MagicMock()
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            result = await github_service.get_user_contribution_stats("johndoe")
            
            assert result["total_recent_events"] == 5
            assert result["push_events"] == 2
            assert result["pull_request_events"] == 1


# ============================================================================
# Complete Profile Tests
# ============================================================================

class TestCompleteProfile:
    """Tests for complete profile aggregation."""
    
    @pytest.fixture
    def github_service(self):
        """Create GitHub service instance."""
        with patch('app.services.github_service.settings') as mock_settings:
            mock_settings.GITHUB_TOKEN = "test-token"
            from app.services.github_service import GitHubService
            return GitHubService()
    
    @pytest.mark.asyncio
    async def test_get_complete_profile_success(self, github_service, sample_github_profile, sample_github_repos):
        """Should aggregate complete profile data."""
        with patch.object(github_service, 'get_user_profile', new_callable=AsyncMock) as mock_profile:
            with patch.object(github_service, 'get_user_repos', new_callable=AsyncMock) as mock_repos:
                with patch.object(github_service, 'get_user_contribution_stats', new_callable=AsyncMock) as mock_stats:
                    with patch.object(github_service, 'get_user_top_languages', new_callable=AsyncMock) as mock_langs:
                        mock_profile.return_value = sample_github_profile
                        mock_repos.return_value = sample_github_repos
                        mock_stats.return_value = {"total_recent_events": 10}
                        mock_langs.return_value = {"Python": 60.0, "JavaScript": 40.0}
                        
                        result = await github_service.get_complete_profile("johndoe")
                        
                        assert "profile" in result
                        assert "top_repos" in result
                        assert "contribution_stats" in result
                        assert "top_languages" in result
                        assert "fetched_at" in result
    
    @pytest.mark.asyncio
    async def test_get_complete_profile_user_not_found(self, github_service):
        """Should return error when user not found."""
        with patch.object(github_service, 'get_user_profile', new_callable=AsyncMock) as mock_profile:
            with patch.object(github_service, 'get_user_repos', new_callable=AsyncMock) as mock_repos:
                with patch.object(github_service, 'get_user_contribution_stats', new_callable=AsyncMock) as mock_stats:
                    mock_profile.return_value = None
                    mock_repos.return_value = []
                    mock_stats.return_value = {}
                    
                    result = await github_service.get_complete_profile("nonexistent")
                    
                    assert "error" in result


# ============================================================================
# Repos to Projects Conversion Tests
# ============================================================================

class TestReposToProjects:
    """Tests for converting repos to project format."""
    
    @pytest.fixture
    def github_service(self):
        """Create GitHub service instance."""
        with patch('app.services.github_service.settings') as mock_settings:
            mock_settings.GITHUB_TOKEN = "test-token"
            from app.services.github_service import GitHubService
            return GitHubService()
    
    def test_repos_to_projects_basic(self, github_service, sample_github_repos):
        """Should convert repos to project format."""
        result = github_service.repos_to_projects(sample_github_repos)
        
        assert len(result) == 2
        assert result[0]["title"] == "Awesome Project"
        assert "Python" in result[0]["technologies"]
        assert result[0]["github_url"] == "https://github.com/johndoe/awesome-project"
    
    def test_repos_to_projects_skips_no_description(self, github_service):
        """Should skip repos without descriptions."""
        repos = [
            {"name": "with-desc", "description": "Has description", "language": "Python", "url": "https://github.com/user/with-desc"},
            {"name": "no-desc", "description": None, "language": "JavaScript", "url": "https://github.com/user/no-desc"}
        ]
        
        result = github_service.repos_to_projects(repos)
        
        assert len(result) == 1
        assert result[0]["title"] == "With Desc"
    
    def test_repos_to_projects_includes_stars_in_bullets(self, github_service):
        """Should include star count in bullet points."""
        repos = [
            {
                "name": "popular-repo",
                "description": "A popular repository",
                "language": "Python",
                "url": "https://github.com/user/popular-repo",
                "stars": 500,
                "forks": 50
            }
        ]
        
        result = github_service.repos_to_projects(repos)
        
        assert any("500" in bullet for bullet in result[0]["bullet_points"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
