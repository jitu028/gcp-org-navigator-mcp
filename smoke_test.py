#!/usr/bin/env python3
"""
Quick smoke-test for the Resource Manager MCP server tools.
Runs the tools directly (no agent) to verify ADC auth + API access.

Usage:
  cd /path/to/sdd-adk-agents-agy
  source .venv/bin/activate
  python resource_manager_mcp/smoke_test.py
"""

import json
import sys
from pathlib import Path

# Make the package importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from resource_manager_mcp.mcp_server import (
    list_organizations,
    list_folders,
    get_folder,
    list_projects,
    search_projects,
    get_project,
)

ORG_ID = "123456789012"
FOLDER_ID = "41699456783"
PROJECT_ID = "gcp-adk-demo-123"


def section(title: str):
    print(f"\n{'═'*60}")
    print(f"  {title}")
    print('═'*60)


def pp(obj):
    print(json.dumps(obj, indent=2, default=str))


if __name__ == "__main__":
    section("1. list_organizations()")
    orgs = list_organizations()
    pp(orgs)

    section(f"2. list_folders(organizations/{ORG_ID})")
    folders = list_folders(f"organizations/{ORG_ID}")
    pp(folders)

    section(f"3. get_folder({FOLDER_ID})")
    folder = get_folder(FOLDER_ID)
    pp(folder)

    section(f"4. list_projects(organizations/{ORG_ID})")
    projects = list_projects(f"organizations/{ORG_ID}")
    pp(projects)

    section(f"5. search_projects('parent:organizations/{ORG_ID}')")
    results = search_projects(f"parent:organizations/{ORG_ID}")
    pp(results)

    section(f"6. get_project({PROJECT_ID})")
    project = get_project(PROJECT_ID)
    pp(project)

    print("\n✅ Smoke test complete!")
