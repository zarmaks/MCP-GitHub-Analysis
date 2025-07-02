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
        
        # Get all files recursively (at least 2 levels deep)
        files = []
        try:
            # Get root files
            contents = repo.get_contents("")
            if isinstance(contents, list):
                for item in contents:
                    if item.type == "file":
                        files.append(item.path)
                    elif item.type == "dir":
                        # Get files from subdirectories (1 level deep)
                        try:
                            subcontents = repo.get_contents(item.path)
                            if isinstance(subcontents, list):
                                for subitem in subcontents:
                                    if subitem.type == "file":
                                        files.append(subitem.path)
                                    elif subitem.type == "dir" and item.path in ['.github', 'docs', 'tests', 'src']:
                                        # For important directories, go one more level deep
                                        try:
                                            subsubcontents = repo.get_contents(subitem.path)
                                            if isinstance(subsubcontents, list):
                                                for subsubitem in subsubcontents:
                                                    if subsubitem.type == "file":
                                                        files.append(subsubitem.path)
                                        except:
                                            pass
                        except:
                            pass
            elif hasattr(contents, 'path'):
                files = [contents.path]
        except Exception:
            pass
        
        return {
            'name': repo.name,
            'description': repo.description,
            'readme': readme_content[:2000],  # Increased to 2000 characters to capture more sections
            'language': repo.language,
            'topics': list(repo.get_topics()),
            'files': files,
            'dependencies': self._extract_dependencies(repo)
        }
    
    def _extract_dependencies(self, repo) -> List[str]:
        """Tries to find dependencies from multiple sources and normalizes names"""
        deps = []
        
        # Check requirements.txt
        try:
            requirements = repo.get_contents("requirements.txt")
            content = requirements.decoded_content.decode('utf-8')
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Extract package name (before ==, >=, etc.)
                    pkg_name = line.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0].strip()
                    deps.append(pkg_name.lower())
        except:
            pass
        
        # Check pyproject.toml
        try:
            pyproject = repo.get_contents("pyproject.toml")
            content = pyproject.decoded_content.decode('utf-8')
            # Simple extraction - could be more sophisticated
            if 'dependencies' in content or 'requires' in content:
                lines = content.split('\n')
                for line in lines:
                    if '"' in line and any(pkg in line for pkg in ['langchain', 'openai', 'faiss', 'chromadb', 'fastapi', 'streamlit']):
                        # Extract package name from quotes
                        if '"' in line:
                            parts = line.split('"')
                            for part in parts:
                                if any(pkg in part for pkg in ['langchain', 'openai', 'faiss', 'chromadb']):
                                    pkg_name = part.split('==')[0].split('>=')[0].strip()
                                    deps.append(pkg_name.lower())
        except:
            pass
        
        # Check Python files for import statements (basic detection)
        try:
            contents = repo.get_contents("")
            if isinstance(contents, list):
                python_files = [f for f in contents if f.name.endswith('.py')][:3]  # Check first 3 Python files
                for py_file in python_files:
                    try:
                        file_content = py_file.decoded_content.decode('utf-8')
                        lines = file_content.split('\n')[:50]  # Check first 50 lines
                        for line in lines:
                            line = line.strip()
                            if line.startswith('import ') or line.startswith('from '):
                                # Extract common ML/AI packages
                                if 'langchain' in line:
                                    deps.append('langchain')
                                elif 'openai' in line:
                                    deps.append('openai')
                                elif 'faiss' in line:
                                    deps.append('faiss')
                                elif 'chromadb' in line:
                                    deps.append('chromadb')
                                elif 'fastapi' in line:
                                    deps.append('fastapi')
                                elif 'streamlit' in line:
                                    deps.append('streamlit')
                    except:
                        continue
        except:
            pass
        
        # Normalize and map package names
        normalized_deps = []
        for dep in deps:
            dep_lower = dep.lower()
            # Map variations to standard names
            if 'langchain' in dep_lower:
                normalized_deps.append('langchain')
            elif 'openai' in dep_lower:
                normalized_deps.append('openai')
            elif 'faiss' in dep_lower:
                normalized_deps.append('vectordb')  # Map to the skill path name
            elif 'chromadb' in dep_lower or 'chroma' in dep_lower:
                normalized_deps.append('vectordb')  # Map to the skill path name
            elif 'fastapi' in dep_lower:
                normalized_deps.append('fastapi')
            else:
                normalized_deps.append(dep_lower)
        
        return list(set(normalized_deps))  # Remove duplicates
    
    def get_languages_summary(self) -> Dict[str, int]:
        """Returns a summary of the languages you use"""
        languages = {}
        for repo in self.user.get_repos():
            if repo.language:
                languages[repo.language] = languages.get(repo.language, 0) + 1
        return languages