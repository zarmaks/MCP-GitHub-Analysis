"""
Simple tests to make sure everything works
"""

import asyncio
from tools import (
    analyze_portfolio,
    analyze_specific_repo,
    analyze_specific_repo_enhanced,
    suggest_improvements,
    find_learning_path
)

async def test_all_tools():
    print("🧪 Testing GitHub Portfolio MCP Tools\n")
    
    # Test 1: Portfolio Analysis
    print("1. Testing Portfolio Analysis...")
    try:
        result = await analyze_portfolio()
        print(f"✅ Found {result['total_repos']} repos")
        print(f"   Languages: {list(result['languages'].keys())}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Repo Analysis
    print("\n2. Testing Repo Analysis...")
    try:
        # Use one of your repos
        result = await analyze_specific_repo("Lightly-GPT")
        print(f"✅ Analyzed {result['repo_name']}")
        print(f"   Type: {result['project_type']}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test 2b: Enhanced Repo Analysis
    print("\n2b. Testing Enhanced Repo Analysis...")
    try:
        result = await analyze_specific_repo_enhanced("Lightly-GPT")
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Enhanced analysis for {result['basic_info']['name']}")
            print(f"   Quality Score: {result['quality_metrics']['quality_score']}/100")
            print(f"   Project Type: {result['project_type']}")
            print(f"   Suggestions: {len(result['suggestions'])}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Improvements
    print("\n3. Testing Improvement Suggestions...")
    try:
        result = await suggest_improvements()
        print(f"✅ Got {result['total_suggestions']} suggestions")
        print(f"   Score: {result['total_score']}/{result['max_possible_score']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Learning Path
    print("\n4. Testing Learning Path...")
    try:
        result = await find_learning_path("llm_engineer")
        print(f"✅ Created path for {result['target']}")
        print(f"   Next project: {result['next_project']}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_all_tools())