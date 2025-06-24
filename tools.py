"""
The tools we will expose via MCP.
Each function is a tool that an LLM can call.
"""

from typing import Dict, List
from github_client import SimpleGitHubClient

# Initialize client
github = SimpleGitHubClient()

async def analyze_portfolio() -> Dict:
    """
    Tool 1: Analyzes the entire portfolio and returns a summary
    """
    repos = github.get_all_repos()
    languages = github.get_languages_summary()
    
    # Find the most popular repos (by stars)
    popular_repos = sorted(repos, key=lambda x: x['stars'], reverse=True)[:3]
    
    # Collect all topics
    all_topics = []
    for repo in repos:
        all_topics.extend(repo['topics'])
    
    # Count project types
    project_types = {
        'ml_projects': len([r for r in repos if any(t in ['machine-learning', 'ml', 'ai'] for t in r['topics'])]),
        'web_projects': len([r for r in repos if r['language'] in ['JavaScript', 'HTML', 'CSS']]),
        'data_projects': len([r for r in repos if 'data' in r['name'].lower() or 'analysis' in r['name'].lower()])
    }
    
    return {
        'total_repos': len(repos),
        'languages': languages,
        'popular_repos': popular_repos,
        'project_types': project_types,
        'unique_topics': list(set(all_topics)),
        'newest_repo': repos[0]['name'] if repos else None
    }

async def analyze_specific_repo(repo_name: str) -> Dict:
    """
    Tool 2: Analyzes a specific repository
    """
    try:
        details = github.get_repo_details(repo_name)
        
        # Try to infer the project type
        project_type = "unknown"
        if any(dep in details['dependencies'] for dep in ['torch', 'tensorflow', 'scikit-learn']):
            project_type = "machine_learning"
        elif any(dep in details['dependencies'] for dep in ['flask', 'django', 'fastapi']):
            project_type = "web_api"
        elif any(dep in details['dependencies'] for dep in ['pandas', 'numpy', 'matplotlib']):
            project_type = "data_analysis"
        
        return {
            'repo_name': details['name'],
            'description': details['description'],
            'main_language': details['language'],
            'project_type': project_type,
            'key_dependencies': details['dependencies'][:5],  # Top 5
            'file_count': len(details['files']),
            'has_readme': len(details['readme']) > 50,
            'topics': details['topics']
        }
    except Exception as e:
        return {'error': f'Repo {repo_name} not found or error: {str(e)}'}

async def suggest_improvements() -> Dict:
    """
    Tool 3: Suggests improvements for the portfolio
    """
    repos = github.get_all_repos()
    
    suggestions = []
    
    # Check for missing READMEs
    for repo in repos:
        details = github.get_repo_details(repo['name'])
        if len(details['readme']) < 100:
            suggestions.append(f"Add detailed README to {repo['name']}")
    
    # Check for missing descriptions
    no_desc = [r['name'] for r in repos if r['description'] == 'No description']
    if no_desc:
        suggestions.append(f"Add descriptions to: {', '.join(no_desc)}")
    
    # Suggest diversification
    languages = github.get_languages_summary()
    if len(languages) < 3:
        suggestions.append("Consider diversifying with more programming languages")
    
    # Check for tests
    has_tests = False
    for repo in repos[:5]:  # Check top 5 repos
        details = github.get_repo_details(repo['name'])
        if any('test' in f.lower() for f in details['files']):
            has_tests = True
            break
    
    if not has_tests:
        suggestions.append("Add unit tests to your main projects")
    
    return {
        'total_suggestions': len(suggestions),
        'suggestions': suggestions,
        'portfolio_score': min(100, len(repos) * 10 + len(languages) * 5),
        'next_steps': "Focus on documentation and testing"
    }

async def find_learning_path(target_skill: str) -> Dict:
    """
    Tool 4: Suggests a learning path based on what you already have
    """
    current_skills = []
    repos = github.get_all_repos()
    
    # Extract current skills from repos
    for repo in repos:
        details = github.get_repo_details(repo['name'])
        current_skills.extend(details['dependencies'])
    
    current_skills = list(set(current_skills))
    
    # Simple skill paths (you can extend this)
    skill_paths = {
        'mlops': {
            'need': ['docker', 'kubernetes', 'mlflow', 'airflow'],
            'projects': ['ml-pipeline', 'model-monitoring', 'ab-testing']
        },
        'llm_engineer': {
            'need': ['langchain', 'openai', 'vectordb', 'fastapi'],
            'projects': ['rag-system', 'agent-framework', 'llm-api']
        },
        'full_stack_ai': {
            'need': ['react', 'nextjs', 'fastapi', 'postgresql'],
            'projects': ['ai-saas-app', 'ml-dashboard', 'prediction-api']
        }
    }
    
    if target_skill not in skill_paths:
        return {'error': f'Unknown skill path: {target_skill}'}
    
    path = skill_paths[target_skill]
    missing_skills = [s for s in path['need'] if s not in current_skills]
    
    return {
        'target': target_skill,
        'current_skills': current_skills[:10],  # Top 10
        'missing_skills': missing_skills,
        'suggested_projects': path['projects'],
        'next_project': path['projects'][0] if path['projects'] else None
    }