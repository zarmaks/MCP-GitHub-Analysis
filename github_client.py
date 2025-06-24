"""
Simple helper to read data from GitHub.
Keep the code simple and readable.
"""

import os
from github import Github
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

class SimpleGitHubClient:
    def __init__(self):
        token = os.getenv('GITHUB_TOKEN')
        self.username = os.getenv('GITHUB_USERNAME', 'zarmaks')
        self.client = Github(token)
        self.user = self.client.get_user(self.username)
    
    def get_all_repos(self) -> List[Dict]:
        """Returns a list with your repos"""
        repos = []
        for repo in self.user.get_repos():
            repos.append({
                'name': repo.name,
                'description': repo.description or 'No description',
                'language': repo.language or 'Unknown',
                'stars': repo.stargazers_count,
                'url': repo.html_url,
                'topics': list(repo.get_topics()),
                'created_at': repo.created_at.isoformat()
            })
        return repos
    
    def get_repo_details(self, repo_name: str) -> Dict:
        """Returns details for a specific repo"""
        repo = self.user.get_repo(repo_name)
        
        # Read README if it exists
        readme_content = ""
        try:
            readme = repo.get_readme()
            readme_content = readme.decoded_content.decode('utf-8')
        except:
            readme_content = "No README found"
        
        # Get all files in the root of the repo
        files = []
        try:
            contents = repo.get_contents("")
            if isinstance(contents, list):
                files = [f.path for f in contents if hasattr(f, 'path')]
            elif hasattr(contents, 'path'):
                files = [contents.path]
        except Exception:
            pass
        
        return {
            'name': repo.name,
            'description': repo.description,
            'readme': readme_content[:500],  # First 500 characters
            'language': repo.language,
            'topics': list(repo.get_topics()),
            'files': files,
            'dependencies': self._extract_dependencies(repo)
        }
    
    def _extract_dependencies(self, repo) -> List[str]:
        """Tries to find dependencies from requirements.txt"""
        deps = []
        try:
            requirements = repo.get_contents("requirements.txt")
            content = requirements.decoded_content.decode('utf-8')
            deps = [line.strip() for line in content.split('\n') if line.strip()]
        except:
            pass
        return deps
    
    def get_languages_summary(self) -> Dict[str, int]:
        """Returns a summary of the languages you use"""
        languages = {}
        for repo in self.user.get_repos():
            if repo.language:
                languages[repo.language] = languages.get(repo.language, 0) + 1
        return languages