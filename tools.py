"""
The tools we will expose via MCP.
Each function is a tool that an LLM can call.
"""

from typing import Dict, List
from github_client import SimpleGitHubClient
from datetime import datetime, timezone

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
    Tool 3: Suggests improvements for the portfolio with detailed score breakdown
    """
    repos = github.get_all_repos()
    languages = github.get_languages_summary()
    
    suggestions = []
    score_breakdown = {}
    
    # 1. Repository Count Analysis
    repo_count = len(repos)
    repo_score = min(50, repo_count * 3.5)  # Max 50 points for repos
    score_breakdown['repositories'] = {
        'score': int(repo_score),
        'max_score': 50,
        'details': f"You have {repo_count} repositories (3.5 points each, max 50)",
        'status': '✅ Excellent' if repo_count >= 14 else '⚠️ Good' if repo_count >= 8 else '❌ Needs more repos'
    }
    
    # 2. Language Diversity Analysis
    language_count = len(languages)
    language_score = min(20, language_count * 5)  # Max 20 points for languages
    score_breakdown['language_diversity'] = {
        'score': int(language_score),
        'max_score': 20,
        'details': f"You use {language_count} programming languages: {', '.join(languages.keys())}",
        'status': '✅ Great diversity' if language_count >= 4 else '⚠️ Good variety' if language_count >= 2 else '❌ Need more languages'
    }
    if language_count < 3:
        suggestions.append("Consider diversifying with more programming languages (JavaScript, Go, etc.)")
    
    # 3. Documentation Quality Analysis
    docs_score = 0
    repos_with_good_readme = 0
    repos_with_description = 0
    
    for repo in repos:
        details = github.get_repo_details(repo['name'])
        
        # Check README quality
        if len(details['readme']) >= 100:
            repos_with_good_readme += 1
        else:
            suggestions.append(f"Improve README for '{repo['name']}' (currently {len(details['readme'])} characters)")
        
        # Check descriptions
        if repo['description'] and repo['description'] != 'No description':
            repos_with_description += 1
        else:
            suggestions.append(f"Add description to '{repo['name']}'")
    
    docs_score = (repos_with_good_readme / repo_count) * 15 + (repos_with_description / repo_count) * 10  # Max 25
    score_breakdown['documentation'] = {
        'score': int(docs_score),
        'max_score': 25,
        'details': f"{repos_with_good_readme}/{repo_count} repos have good READMEs, {repos_with_description}/{repo_count} have descriptions",
        'status': '✅ Well documented' if docs_score >= 20 else '⚠️ Needs improvement' if docs_score >= 10 else '❌ Poor documentation'
    }
    
    # 4. Code Quality Analysis (Tests)
    has_tests = False
    repos_with_tests = 0
    
    for repo in repos[:10]:  # Check more repos for tests
        details = github.get_repo_details(repo['name'])
        if any('test' in f.lower() for f in details['files']):
            has_tests = True
            repos_with_tests += 1
    
    test_score = min(5, repos_with_tests * 1)  # Max 5 points for testing
    score_breakdown['code_quality'] = {
        'score': int(test_score),
        'max_score': 5,
        'details': f"{repos_with_tests}/{min(10, repo_count)} repos have tests",
        'status': '✅ Good testing' if repos_with_tests >= 3 else '⚠️ Some testing' if repos_with_tests >= 1 else '❌ No tests found'
    }
    
    if not has_tests:
        suggestions.append("Add unit tests to your main projects (pytest, unittest)")
    
    # Calculate total score
    total_score = (
        score_breakdown['repositories']['score'] +
        score_breakdown['language_diversity']['score'] +
        score_breakdown['documentation']['score'] +
        score_breakdown['code_quality']['score']
    )
    
    # Create summary of strengths
    strengths = []
    if score_breakdown['repositories']['score'] >= 40:
        strengths.append("📈 Strong repository portfolio")
    if score_breakdown['language_diversity']['score'] >= 15:
        strengths.append("🌍 Good language diversity")
    if score_breakdown['documentation']['score'] >= 20:
        strengths.append("📚 Well-documented projects")
    if score_breakdown['code_quality']['score'] >= 3:
        strengths.append("🧪 Uses testing practices")
    
    # Areas for improvement
    areas_for_improvement = []
    if score_breakdown['repositories']['score'] < 30:
        areas_for_improvement.append("Create more repositories")
    if score_breakdown['language_diversity']['score'] < 15:
        areas_for_improvement.append("Learn additional programming languages")
    if score_breakdown['documentation']['score'] < 15:
        areas_for_improvement.append("Improve documentation quality")
    if score_breakdown['code_quality']['score'] < 2:
        areas_for_improvement.append("Add testing to projects")
    
    return {
        'total_score': int(total_score),
        'max_possible_score': 100,
        'score_breakdown': score_breakdown,
        'strengths': strengths,
        'areas_for_improvement': areas_for_improvement,
        'total_suggestions': len(suggestions),
        'suggestions': suggestions[:10],  # Limit to top 10 suggestions
        'next_steps': f"Focus on {areas_for_improvement[0] if areas_for_improvement else 'maintaining current quality'}"
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

async def analyze_specific_repo_enhanced(repo_name: str) -> Dict:
    """
    Enhanced repository analysis με πολλά περισσότερα insights
    """
    try:
        # Get basic details
        details = github.get_repo_details(repo_name)
        repo = github.user.get_repo(repo_name)
        
        # 1. Basic Info (existing)
        basic_info = {
            'name': details['name'],
            'description': details['description'],
            'main_language': details['language'],
            'topics': details['topics'],
            'url': repo.html_url,
            'created_at': repo.created_at.isoformat(),
            'last_updated': repo.updated_at.isoformat()
        }
        
        # 2. Code Quality
        quality_metrics = {
            'has_tests': any('test' in f.lower() for f in details['files']),
            'has_docs': any('docs' in f.lower() for f in details['files']),
            'has_ci': any('.github/workflows/' in f or '.travis.yml' in f or '.gitlab-ci.yml' in f for f in details['files']),
            'has_gitignore': '.gitignore' in details['files'],
            'has_license': any('LICENSE' in f or 'license' in f.lower() for f in details['files']) or 'license' in details['readme'].lower()
        }
        # Calculate quality_score separately
        quality_score = sum(1 for v in quality_metrics.values() if v) * 20  # 0-100
        
        # 3. Project Structure
        structure_analysis = {
            'total_files': len(details['files']),
            'has_proper_structure': check_project_structure(details['files']),
            'main_directories': extract_main_dirs(details['files']),
            'file_types': count_file_types(details['files'])
        }
        
        # 4. Dependencies Deep Dive
        deps_analysis = {
            'total_dependencies': len(details['dependencies']),
            'main_frameworks': identify_frameworks(details['dependencies']),
            'dependency_categories': categorize_dependencies(details['dependencies']),
            'complexity_level': assess_complexity(details['dependencies'])
        }
        
        # 5. README Analysis
        readme_analysis = {
            'readme_length': len(details['readme']),
            'has_badges': '![' in details['readme'] or '[![' in details['readme'],
            'sections_found': extract_sections(details['readme']),
            'has_installation': any(keyword in details['readme'].lower() for keyword in ['installation', 'install', 'setup', 'getting started']),
            'has_usage': any(keyword in details['readme'].lower() for keyword in ['usage', 'example', 'how to use']),
            'readme_quality': 'excellent' if len(details['readme']) > 2000 else 'good' if len(details['readme']) > 1000 else 'needs_improvement'
        }
        
        # 6. Activity & Maintenance
        commits = list(repo.get_commits())[:10]
        activity_analysis = {
            'total_commits': repo.get_commits().totalCount,
            'recent_commits': len(commits),
            'last_commit': commits[0].commit.author.date.isoformat() if commits else None,
            'is_active': (datetime.now(timezone.utc) - repo.updated_at).days < 90,
            'contributors': repo.get_contributors().totalCount
        }
        
        # 7. Project Type & Purpose
        project_classification = classify_project_enhanced(
            details['dependencies'],
            details['files'],
            details['readme'],
            details['topics']
        )
        
        # 8. Improvement Suggestions
        suggestions = generate_repo_suggestions(
            {**quality_metrics, 'quality_score': quality_score},
            structure_analysis,
            readme_analysis,
            activity_analysis
        )
        
        # 9. Learning Value
        learning_insights = {
            'technologies_used': list(set(deps_analysis['main_frameworks'])),
            'skill_level': assess_skill_level(structure_analysis, deps_analysis),
            'portfolio_value': calculate_portfolio_value({**quality_metrics, 'quality_score': quality_score}, activity_analysis),
            'interview_talking_points': generate_talking_points(project_classification, deps_analysis)
        }
        
        # Combine all analyses
        return {
            'basic_info': basic_info,
            'quality_metrics': {**quality_metrics, 'quality_score': quality_score},
            'structure': structure_analysis,
            'dependencies': deps_analysis,
            'readme': readme_analysis,
            'activity': activity_analysis,
            'project_type': project_classification,
            'suggestions': suggestions,
            'learning_insights': learning_insights,
            'overall_score': calculate_overall_score({**quality_metrics, 'quality_score': quality_score}, activity_analysis, readme_analysis)
        }
        
    except Exception as e:
        return {'error': f'Failed to analyze {repo_name}: {str(e)}'}

# Helper functions

def check_project_structure(files):
    """Check if project has good structure"""
    good_patterns = ['src/', 'tests/', 'docs/', 'README']
    return sum(any(pattern in f for f in files) for pattern in good_patterns) >= 2

def extract_main_dirs(files):
    """Extract main directories"""
    dirs = set()
    for f in files:
        if '/' in f:
            dirs.add(f.split('/')[0])
    return list(dirs)[:5]  # Top 5

def count_file_types(files):
    """Count different file types"""
    extensions = {}
    for f in files:
        if '.' in f:
            ext = f.split('.')[-1]
            extensions[ext] = extensions.get(ext, 0) + 1
    return dict(sorted(extensions.items(), key=lambda x: x[1], reverse=True)[:5])

def identify_frameworks(dependencies):
    """Identify main frameworks from dependencies"""
    frameworks = {
        'torch': 'PyTorch',
        'tensorflow': 'TensorFlow',
        'django': 'Django',
        'flask': 'Flask',
        'fastapi': 'FastAPI',
        'langchain': 'LangChain',
        'streamlit': 'Streamlit',
        'pandas': 'Pandas',
        'scikit-learn': 'Scikit-learn'
    }
    found = []
    for dep in dependencies:
        dep_lower = dep.lower()
        for key, name in frameworks.items():
            if key in dep_lower:
                found.append(name)
    return found

def categorize_dependencies(dependencies):
    """Categorize dependencies by type"""
    categories = {
        'ml': ['torch', 'tensorflow', 'keras', 'scikit-learn'],
        'data': ['pandas', 'numpy', 'scipy', 'matplotlib'],
        'web': ['flask', 'django', 'fastapi', 'requests'],
        'llm': ['openai', 'langchain', 'transformers', 'anthropic'],
        'testing': ['pytest', 'unittest', 'mock', 'coverage'],
        'utils': ['click', 'tqdm', 'python-dotenv', 'pyyaml']
    }
    
    found_categories = {}
    for cat, keywords in categories.items():
        matching = [d for d in dependencies if any(k in d.lower() for k in keywords)]
        if matching:
            found_categories[cat] = len(matching)
    
    return found_categories

def assess_complexity(dependencies):
    """Assess project complexity based on dependencies"""
    if len(dependencies) < 5:
        return 'simple'
    elif len(dependencies) < 15:
        return 'medium'
    else:
        return 'complex'

def extract_sections(readme_content):
    """Extract sections from README"""
    sections = []
    readme_lower = readme_content.lower()
    
    # Check for common sections
    section_patterns = {
        'headers': ['##', '###', '#'],  # Markdown headers
        'installation': ['installation', 'install', 'setup', 'getting started', 'quick start', 'clone and setup'],
        'usage': ['usage', 'example', 'how to use', 'quickstart', 'example queries', 'run the app'],
        'features': ['features', 'functionality'],
        'requirements': ['requirements', 'dependencies', 'prerequisites'],
        'license': ['license', 'licensing'],
        'contributing': ['contributing', 'contribution', 'contributors', 'development'],
        'documentation': ['documentation', 'docs'],
        'testing': ['testing', 'tests', 'test', 'run tests'],
        'api': ['api', 'reference'],
        'acknowledgments': ['acknowledgments', 'thanks', 'credits']
    }
    
    for section_name, keywords in section_patterns.items():
        if any(keyword in readme_lower for keyword in keywords):
            sections.append(section_name)
    
    return sections

def classify_project_enhanced(deps, files, readme, topics):
    """Enhanced project classification"""
    # Check multiple signals
    signals = {
        'machine_learning': 0,
        'web_application': 0,
        'data_analysis': 0,
        'api_service': 0,
        'cli_tool': 0,
        'library': 0
    }
    
    # Check dependencies
    ml_deps = ['torch', 'tensorflow', 'scikit-learn', 'keras']
    web_deps = ['flask', 'django', 'fastapi', 'streamlit']
    data_deps = ['pandas', 'numpy', 'matplotlib', 'seaborn']
    
    for dep in deps:
        dep_lower = dep.lower()
        if any(ml in dep_lower for ml in ml_deps):
            signals['machine_learning'] += 2
        if any(web in dep_lower for web in web_deps):
            signals['web_application'] += 2
        if any(data in dep_lower for data in data_deps):
            signals['data_analysis'] += 1
    
    # Check files
    if any('api' in f.lower() or 'route' in f.lower() for f in files):
        signals['api_service'] += 2
    if any('cli' in f.lower() or 'main.py' in f.lower() for f in files):
        signals['cli_tool'] += 1
    if 'setup.py' in files or 'pyproject.toml' in files:
        signals['library'] += 2
    
    # Check topics
    for topic in topics:
        if 'machine-learning' in topic or 'ml' in topic:
            signals['machine_learning'] += 1
        if 'web' in topic or 'api' in topic:
            signals['web_application'] += 1
    
    # Return the highest scoring type
    if max(signals.values()) == 0:
        return 'general'
    
    return max(signals.items(), key=lambda x: x[1])[0]

def generate_repo_suggestions(quality, structure, readme, activity):
    """Generate specific suggestions for improvement"""
    suggestions = []
    
    # Quality suggestions
    if not quality['has_tests']:
        suggestions.append({
            'priority': 'high',
            'category': 'quality',
            'suggestion': 'Add unit tests using pytest',
            'impact': 'Improves reliability and maintainability'
        })
    
    if not quality['has_ci']:
        suggestions.append({
            'priority': 'medium',
            'category': 'automation',
            'suggestion': 'Add GitHub Actions for CI/CD',
            'impact': 'Automates testing and deployment'
        })
    
    # README suggestions
    if readme['readme_quality'] == 'needs_improvement':
        suggestions.append({
            'priority': 'high',
            'category': 'documentation',
            'suggestion': 'Expand README with installation, usage, and examples',
            'impact': 'Makes project more accessible'
        })
    elif not readme['has_installation']:
        suggestions.append({
            'priority': 'medium',
            'category': 'documentation',
            'suggestion': 'Add installation instructions to README',
            'impact': 'Helps users get started quickly'
        })
    elif not readme['has_usage']:
        suggestions.append({
            'priority': 'medium',
            'category': 'documentation',
            'suggestion': 'Add usage examples to README',
            'impact': 'Shows users how to use your project'
        })
    
    # Activity suggestions
    if not activity['is_active']:
        suggestions.append({
            'priority': 'low',
            'category': 'maintenance',
            'suggestion': 'Update dependencies and refactor old code',
            'impact': 'Keeps project current and secure'
        })
    
    return suggestions

def assess_skill_level(structure, deps):
    """Assess skill level demonstrated in project"""
    score = 0
    
    # Structure points
    if structure['has_proper_structure']:
        score += 20
    if structure['total_files'] > 10:
        score += 10
    
    # Dependency complexity
    if deps['complexity_level'] == 'complex':
        score += 30
    elif deps['complexity_level'] == 'medium':
        score += 20
    
    # Advanced frameworks
    if any(f in ['PyTorch', 'TensorFlow', 'LangChain'] for f in deps['main_frameworks']):
        score += 20
    
    if score < 30:
        return 'beginner'
    elif score < 60:
        return 'intermediate'
    else:
        return 'advanced'

def calculate_portfolio_value(quality, activity):
    """Calculate how valuable this project is for portfolio"""
    value = quality['quality_score']
    
    if activity['is_active']:
        value += 20
    if activity['contributors'] > 1:
        value += 10
    
    if value >= 80:
        return 'high'
    elif value >= 50:
        return 'medium'
    else:
        return 'low'

def generate_talking_points(project_type, deps):
    """Generate interview talking points"""
    points = []
    
    points.append(f"Built a {project_type.replace('_', ' ')} project")
    
    if deps['main_frameworks']:
        points.append(f"Implemented using {', '.join(deps['main_frameworks'][:3])}")
    
    if deps['complexity_level'] == 'complex':
        points.append("Managed complex dependency architecture")
    
    if 'ml' in deps['dependency_categories']:
        points.append("Applied machine learning techniques")
    
    if 'testing' in deps['dependency_categories']:
        points.append("Implemented comprehensive testing")
    
    return points[:4]  # Top 4 points

def calculate_overall_score(quality, activity, readme):
    """Calculate overall repository score"""
    score = 0
    
    # Quality (40%)
    score += quality['quality_score'] * 0.4
    
    # Activity (30%)
    if activity['is_active']:
        score += 30
    
    # Documentation (30%)
    if readme['readme_quality'] == 'good':
        score += 30
    elif readme['readme_quality'] == 'needs_improvement':
        score += 15
    
    return int(score)