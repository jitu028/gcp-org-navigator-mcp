"""
GCP Org Navigator Agent
=======================
An ADK agent that uses the Resource Manager MCP server to navigate
and query GCP organization resources: orgs, folders, and projects.

Usage:
  cd resource_manager_mcp/
  uv run adk web   (then chat with the agent in the browser)
  # or
  uv run adk run org_navigator
"""

import os
import sys
from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import MCPToolset, StdioConnectionParams
from mcp import StdioServerParameters

# Path to the MCP server script (sibling file in the same package)
_SERVER_SCRIPT = str(Path(__file__).parent / "mcp_server.py")

# Use the Python interpreter from the current virtual environment
_PYTHON = sys.executable

# ─── MCP Toolset — spawns mcp_server.py as a child process ───────────────────
resource_manager_tools = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=_PYTHON,
            args=[_SERVER_SCRIPT],
        )
    )
)

# ─── ADK Agent ────────────────────────────────────────────────────────────────
root_agent = LlmAgent(
    name="org_navigator",
    model="gemini-2.5-flash",
    description=(
        "GCP Organization Navigator — explores the resource hierarchy "
        "(organizations, folders, projects) and IAM policies using the "
        "Cloud Resource Manager API."
    ),
    instruction="""
You are an expert GCP Organization Navigator. Your job is to help users
understand and explore their GCP resource hierarchy.

Your capabilities (via MCP tools):
- list_organizations       → orgs the caller can access
- list_folders(parent)     → folders under an org or parent folder
- get_folder(folder_id)    → details of a specific folder
- list_projects(parent)    → projects under an org or folder
- search_projects(query)   → search projects org-wide with filters
- get_project(project_id)  → details of a specific project
- get_org_iam_policy(org_id)       → org-level IAM bindings
- get_project_iam_policy(project_id) → project-level IAM bindings

Guidelines:
1. Always start by calling list_organizations to confirm what org is accessible.
2. Use list_folders with "organizations/<id>" to explore top-level structure.
3. For broad searches, prefer search_projects over list_projects.
4. When presenting IAM policies, group by role and highlight privileged bindings
   (roles/owner, roles/editor, roles/resourcemanager.*).
5. Format results as clean markdown tables where possible.
6. If a user asks about a project or folder by name, search for it first.
7. Be concise but complete. Highlight anomalies or potential misconfigurations.
""",
    tools=[resource_manager_tools],
)
