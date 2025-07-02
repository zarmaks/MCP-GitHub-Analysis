"""
Debug script to test dependency detection
"""
import asyncio
from github_client import SimpleGitHubClient
from tools import find_learning_path

async def debug_dependencies():
    print("🔍 Debug: Testing dependency detection...")
    
    try:
        # Test GitHub client
        github = SimpleGitHubClient()
        repos = github.get_all_repos()
        print(f"✅ Found {len(repos)} repos")
        
        # Test dependency extraction for ALL repos with dependencies
        print("\n📦 Checking dependencies in ALL repos:")
        repos_with_deps = 0
        all_dependencies = []
        
        for repo in repos:  # Check ALL repos
            details = github.get_repo_details(repo['name'])
            all_dependencies.extend(details['dependencies'])
            if details['dependencies']:
                repos_with_deps += 1
                print(f"  📁 {repo['name']}: {details['dependencies'][:5]}{'...' if len(details['dependencies']) > 5 else ''}")
        
        print(f"\n📊 Summary: {repos_with_deps}/{len(repos)} repos have dependencies")
        unique_deps = list(set(all_dependencies))
        print(f"� All unique dependencies: {unique_deps[:20]}{'...' if len(unique_deps) > 20 else ''}")
        
        # Test learning path
        print("\n🎯 Testing llm_engineer learning path...")
        result = await find_learning_path("llm_engineer")
        
        print(f"Current skills found: {result['current_skills'][:10]}")
        print(f"Missing skills: {result['missing_skills']}")
        print(f"Next project: {result['next_project']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_dependencies())
