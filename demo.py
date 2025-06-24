"""
Simple Streamlit app to test the MCP server
"""

import streamlit as st
import json
from github_client import SimpleGitHubClient
import asyncio
from tools import (
    analyze_portfolio,
    analyze_specific_repo,
    suggest_improvements,
    find_learning_path
)

st.title("🚀 GitHub Portfolio MCP Demo")
st.markdown("Test your MCP server tools here!")

# Sidebar
st.sidebar.header("Tools")
tool_choice = st.sidebar.selectbox(
    "Choose a tool:",
    ["Portfolio Analysis", "Repo Analysis", "Get Improvements", "Learning Path"]
)

# Main area
if tool_choice == "Portfolio Analysis":
    st.header("📊 Portfolio Analysis")
    if st.button("Analyze My Portfolio"):
        with st.spinner("Analyzing..."):
            result = asyncio.run(analyze_portfolio())
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Repos", result['total_repos'])
            with col2:
                st.metric("Languages", len(result['languages']))
            
            st.subheader("Language Distribution")
            st.bar_chart(result['languages'])
            
            st.subheader("Popular Repos")
            for repo in result['popular_repos']:
                st.write(f"⭐ {repo['stars']} - [{repo['name']}]({repo['url']})")

elif tool_choice == "Repo Analysis":
    st.header("🔍 Repository Analysis")
    github = SimpleGitHubClient()
    repos = github.get_all_repos()
    repo_names = [r['name'] for r in repos]
    
    selected_repo = st.selectbox("Select a repo:", repo_names)
    if selected_repo is not None and st.button("Analyze Repo"):
        with st.spinner(f"Analyzing {selected_repo}..."):
            result = asyncio.run(analyze_specific_repo(selected_repo))
            
            st.subheader("Repository Details")
            st.write(f"**Type:** {result['project_type']}")
            st.write(f"**Language:** {result['main_language']}")
            st.write(f"**Files:** {result['file_count']}")
            
            if result['key_dependencies']:
                st.subheader("Key Dependencies")
                for dep in result['key_dependencies']:
                    st.write(f"- {dep}")

elif tool_choice == "Get Improvements":
    st.header("💡 Portfolio Improvements")
    if st.button("Get Suggestions"):
        with st.spinner("Analyzing portfolio..."):
            result = asyncio.run(suggest_improvements())
            
            st.metric("Portfolio Score", f"{result['portfolio_score']}/100")
            
            st.subheader("Suggestions")
            for i, suggestion in enumerate(result['suggestions'], 1):
                st.write(f"{i}. {suggestion}")
            
            st.info(result['next_steps'])

elif tool_choice == "Learning Path":
    st.header("🎯 Learning Path Suggester")
    skill = st.selectbox(
        "Choose target role:",
        ["mlops", "llm_engineer", "full_stack_ai"]
    )
    
    if skill is not None and st.button("Get Learning Path"):
        with st.spinner("Creating learning path..."):
            result = asyncio.run(find_learning_path(skill))
            
            if 'error' not in result:
                st.subheader(f"Path to {result['target']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**You have:**")
                    for skill in result['current_skills'][:5]:
                        st.write(f"✅ {skill}")
                
                with col2:
                    st.write("**You need:**")
                    for skill in result['missing_skills']:
                        st.write(f"❌ {skill}")
                
                st.subheader("Suggested Projects")
                for project in result['suggested_projects']:
                    st.write(f"- {project}")

# Run with: streamlit run demo.py