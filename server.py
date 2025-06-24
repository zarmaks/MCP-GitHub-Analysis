"""
Main MCP Server - This is the main file
Start your implementation from here
"""

import asyncio
import os
from mcp.server import Server
from mcp.server.stdio import stdio_server
from dotenv import load_dotenv
from typing import Dict

# Import our tools
from tools import (
    analyze_portfolio,
    analyze_specific_repo,
    suggest_improvements,
    find_learning_path
)

load_dotenv()

# Create server instance
server = Server("github-portfolio-mcp")

# Register Tool 1: Portfolio Analysis
async def analyze_my_portfolio() -> Dict:
    """
    Analyzes your entire GitHub portfolio and returns insights.
    Returns: Summary of repos, languages, and project types.
    """
    return await analyze_portfolio()

# Register Tool 2: Repo Analysis  
async def analyze_repo(repo_name: str) -> Dict:
    """
    Analyzes a specific repository in detail.
    Args:
        repo_name: Name of the repository to analyze
    Returns: Detailed analysis including dependencies and structure.
    """
    return await analyze_specific_repo(repo_name)

# Register Tool 3: Improvement Suggestions
async def get_portfolio_improvements() -> Dict:
    """
    Suggests improvements for your GitHub portfolio.
    Returns: List of actionable suggestions and portfolio score.
    """
    return await suggest_improvements()

# Register Tool 4: Learning Path
async def suggest_learning_path(skill: str) -> Dict:
    """
    Suggests a learning path based on your current skills.
    Args:
        skill: Target skill (mlops, llm_engineer, full_stack_ai)
    Returns: Missing skills and suggested projects.
    """
    return await find_learning_path(skill)

# Run the server
async def main():
    """Start the MCP server"""
    print(f"Starting GitHub Portfolio MCP Server...")
    print(f"Username: {os.getenv('GITHUB_USERNAME')}")
    print(f"Available tools:")
    print("  - analyze_my_portfolio()")
    print("  - analyze_repo(repo_name)")
    print("  - get_portfolio_improvements()")
    print("  - suggest_learning_path(skill)")
    
    # Run server
    async with stdio_server() as streams:
        await server.run(
            streams[0],  # stdin
            streams[1],  # stdout
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())