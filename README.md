# GitHub Portfolio MCP

🚀 **GitHub Portfolio MCP** is a tool that lets you analyze your GitHub portfolio, get improvement suggestions, and design your learning path—all via an MCP (Model Context Protocol) server and a simple Streamlit demo UI.

## Description

This repository includes:
- **MCP Server** with portfolio analysis tools
- **Streamlit Demo App** for easy tool testing
- **Automated improvement and learning path suggestions**

## Features
- Analyze your entire GitHub portfolio (languages, popular repos, project types)
- Deep-dive into a specific repository (dependencies, structure, code quality)
- Automated improvement suggestions (documentation, testing, diversification)
- Learning path suggestions based on your target role (e.g. MLOps, LLM Engineer)

## Files & Structure
- `server.py`: MCP server with all tools
- `tools.py`: All portfolio analysis logic
- `github_client.py`: Simple GitHub API client
- `demo.py`: Streamlit app for tool testing
- `requirements.txt`: Required packages
- `test_server.py`: Simple tests for the tools

## Usage Instructions

1. **Clone the repo**

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
```

2. **Set up your secrets**

Create a `.env` file with:
```
GITHUB_TOKEN=your_github_token
GITHUB_USERNAME=your_github_username
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Run the MCP server**

```bash
python server.py
```

5. **Open the demo UI**

```bash
streamlit run demo.py
```
