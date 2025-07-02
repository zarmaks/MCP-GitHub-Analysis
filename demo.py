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
    analyze_specific_repo_enhanced,  # <-- import the enhanced analyzer
    suggest_improvements,
    find_learning_path
)

st.title("🚀 GitHub Portfolio MCP Demo")
st.markdown("Test your MCP server tools here!")

# Debug info (remove after fixing)
import os
st.sidebar.write("**Debug Info:**")
st.sidebar.write(f"GitHub Token: {'✅ Set' if os.getenv('GITHUB_TOKEN') else '❌ Missing'}")
st.sidebar.write(f"GitHub Username: {os.getenv('GITHUB_USERNAME', 'Not set')}")

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
            try:
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
            except Exception as e:
                st.error(f"Error analyzing portfolio: {str(e)}")
                st.write("**Possible solutions:**")
                st.write("1. Check if your GitHub token is set correctly in .env file")
                st.write("2. Make sure you have internet connection")
                st.write("3. Check if GitHub API rate limit is exceeded")

elif tool_choice == "Repo Analysis":
    st.header("🔍 Repository Analysis")
    try:
        github = SimpleGitHubClient()
        repos = github.get_all_repos()
        repo_names = [r['name'] for r in repos]
        
        selected_repo = st.selectbox("Select a repo:", repo_names)
        if selected_repo is not None and st.button("Analyze Repo"):
            with st.spinner(f"Analyzing {selected_repo}..."):
                try:
                    result = asyncio.run(analyze_specific_repo_enhanced(selected_repo))
                    
                    if 'error' in result:
                        st.error(f"Error: {result['error']}")
                    else:
                        # Display results in tabs
                        tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Quality", "Insights", "Suggestions"])
                        
                        with tab1:
                            st.subheader("Basic Information")
                            info = result['basic_info']
                            st.write(f"**Language:** {info['main_language']}")
                            st.write(f"**Created:** {info['created_at'][:10]}")
                            st.write(f"**Topics:** {', '.join(info['topics'])}")
                            
                            st.subheader("Project Classification")
                            st.info(f"Type: {result['project_type']}")
                        
                        with tab2:
                            st.subheader("Quality Metrics")
                            quality = result['quality_metrics']
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Quality Score", f"{quality['quality_score']}/100")
                            with col2:
                                st.metric("Activity", "Active ✅" if result['activity']['is_active'] else "Inactive ⚠️")
                            
                            # Quality checklist
                            st.write("**Quality Checklist:**")
                            checklist_items = {
                                'has_tests': 'Unit Tests',
                                'has_docs': 'Documentation',
                                'has_ci': 'CI/CD Pipeline',
                                'has_gitignore': 'Git Ignore File',
                                'has_license': 'License'
                            }
                            for key, label in checklist_items.items():
                                if key in quality:
                                    st.write(f"{'✅' if quality[key] else '❌'} {label}")
                            
                            # README quality
                            st.write("**README Quality:**")
                            readme = result['readme']
                            st.write(f"{'✅' if readme['has_installation'] else '❌'} Installation Instructions")
                            st.write(f"{'✅' if readme['has_usage'] else '❌'} Usage Examples")
                            st.write(f"Length: {readme['readme_length']} characters ({readme['readme_quality']})")
                        
                        with tab3:
                            st.subheader("Learning Insights")
                            insights = result['learning_insights']
                            st.write(f"**Skill Level:** {insights['skill_level']}")
                            st.write(f"**Portfolio Value:** {insights['portfolio_value']}")
                            
                            st.write("**Technologies Used:**")
                            for tech in insights['technologies_used']:
                                st.write(f"- {tech}")
                            
                            st.write("**Interview Talking Points:**")
                            for point in insights['interview_talking_points']:
                                st.write(f"• {point}")
                        
                        with tab4:
                            st.subheader("Improvement Suggestions")
                            for suggestion in result['suggestions']:
                                with st.expander(f"{suggestion['priority'].title()} Priority - {suggestion['category'].title()}"):
                                    st.write(f"**{suggestion['suggestion']}**")
                                    st.write(f"Impact: {suggestion['impact']}")
                except Exception as e:
                    st.error(f"Error analyzing repository: {str(e)}")
                    st.write("**Possible solutions:**")
                    st.write("1. Check if the repository exists and is accessible")
                    st.write("2. Check if your GitHub token has proper permissions")
    except Exception as e:
        st.error(f"Error loading repositories: {str(e)}")
        st.write("**Possible solutions:**")
        st.write("1. Check if your GitHub token is set correctly in .env file")
        st.write("2. Make sure you have internet connection")

elif tool_choice == "Get Improvements":
    st.header("💡 Portfolio Improvements")
    if st.button("Get Suggestions"):
        with st.spinner("Analyzing portfolio..."):
            try:
                result = asyncio.run(suggest_improvements())
                
                if 'error' in result:
                    st.error(f"Error: {result['error']}")
                else:
                    # Main score display
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Portfolio Score", f"{result['total_score']}/{result['max_possible_score']}")
                    with col2:
                        percentage = int((result['total_score'] / result['max_possible_score']) * 100)
                        st.metric("Percentage", f"{percentage}%")
                    
                    # Score breakdown in tabs
                    tab1, tab2, tab3 = st.tabs(["📊 Score Breakdown", "💪 Strengths", "📝 Suggestions"])
                    
                    with tab1:
                        st.subheader("Detailed Score Analysis")
                        
                        # Show each category
                        for category, data in result['score_breakdown'].items():
                            with st.expander(f"{category.replace('_', ' ').title()} - {data['score']}/{data['max_score']} points"):
                                st.write(f"**Status:** {data['status']}")
                                st.write(f"**Details:** {data['details']}")
                                
                                # Progress bar
                                progress = data['score'] / data['max_score']
                                st.progress(progress)
                    
                    with tab2:
                        st.subheader("Your Strengths 💪")
                        if result['strengths']:
                            for strength in result['strengths']:
                                st.write(f"• {strength}")
                        else:
                            st.info("Work on the suggestions below to build your strengths!")
                        
                        if result['areas_for_improvement']:
                            st.subheader("Areas for Improvement 🎯")
                            for area in result['areas_for_improvement']:
                                st.write(f"• {area}")
                    
                    with tab3:
                        st.subheader("Actionable Suggestions")
                        if result['suggestions']:
                            for i, suggestion in enumerate(result['suggestions'], 1):
                                st.write(f"{i}. {suggestion}")
                        else:
                            st.success("🎉 No suggestions - your portfolio looks great!")
                        
                        if result['next_steps']:
                            st.info(f"**Next Steps:** {result['next_steps']}")
            except Exception as e:
                st.error(f"Error analyzing portfolio: {str(e)}")
                st.write("**Possible solutions:**")
                st.write("1. Check if your GitHub token is set correctly in .env file")
                st.write("2. Make sure you have internet connection")
                st.write("3. Check if GitHub API rate limit is exceeded")

elif tool_choice == "Learning Path":
    st.header("🎯 Learning Path Suggester")
    skill = st.selectbox(
        "Choose target role:",
        ["mlops", "llm_engineer", "full_stack_ai"]
    )
    
    if skill is not None and st.button("Get Learning Path"):
        with st.spinner("Creating learning path..."):
            try:
                result = asyncio.run(find_learning_path(skill))
                
                if 'error' in result:
                    st.error(f"Error: {result['error']}")
                else:
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
            except Exception as e:
                st.error(f"Error creating learning path: {str(e)}")
                st.write("**Possible solutions:**")
                st.write("1. Check if your GitHub token is set correctly in .env file")
                st.write("2. Make sure you have internet connection")

# Run with: streamlit run demo.py