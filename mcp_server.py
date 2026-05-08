"""
GCP Resource Manager MCP Server (Org-Level)
============================================
Exposes org-level Resource Manager operations as MCP tools:
  - list_organizations      → get orgs the caller has access to
  - list_folders            → list folders under an org or parent folder
  - get_folder              → describe a specific folder
  - list_projects           → list projects under an org / folder
  - search_projects         → search projects by query across the org
  - get_project             → describe a specific project
  - get_org_iam_policy      → fetch IAM policy on the org node
  - get_project_iam_policy  → fetch IAM policy on a project

Authentication: uses Application Default Credentials (ADC).
Run:  python mcp_server.py
"""

from mcp.server.fastmcp import FastMCP
from google.cloud import resourcemanager_v3
from google.iam.v1 import iam_policy_pb2

mcp = FastMCP("gcp-resource-manager")

# ─── Org ──────────────────────────────────────────────────────────────────────

@mcp.tool()
def list_organizations() -> list[dict]:
    """List all GCP organizations the caller has access to.

    Returns a list of organizations with name, display_name, and lifecycle_state.
    Requires resourcemanager.organizations.search on the org.
    """
    client = resourcemanager_v3.OrganizationsClient()
    orgs = []
    for org in client.search_organizations():
        orgs.append({
            "name": org.name,                          # e.g. "organizations/123456789012"
            "display_name": org.display_name,
            "lifecycle_state": org.state.name,
            "directory_customer_id": org.directory_customer_id,
        })
    return orgs


@mcp.tool()
def get_org_iam_policy(org_id: str) -> dict:
    """Fetch the IAM policy attached to a GCP organization node.

    Args:
        org_id: Numeric org ID (e.g. "123456789012") or full resource name
                "organizations/123456789012".

    Returns:
        Bindings list with role → members mappings.
    Requires resourcemanager.organizations.getIamPolicy on the org.
    """
    if not org_id.startswith("organizations/"):
        org_id = f"organizations/{org_id}"

    client = resourcemanager_v3.OrganizationsClient()
    request = iam_policy_pb2.GetIamPolicyRequest(resource=org_id)
    policy = client.get_iam_policy(request=request)

    bindings = []
    for b in policy.bindings:
        bindings.append({"role": b.role, "members": list(b.members)})
    return {"resource": org_id, "bindings": bindings, "etag": policy.etag.hex()}


# ─── Folders ──────────────────────────────────────────────────────────────────

@mcp.tool()
def list_folders(parent: str) -> list[dict]:
    """List folders directly under an organization or a parent folder.

    Args:
        parent: Resource name of the parent. Examples:
                "organizations/123456789012"   ← top-level folders in the org
                "folders/41699456783"          ← sub-folders inside a folder

    Returns:
        List of folders with name, display_name, parent, and lifecycle_state.
    Requires resourcemanager.folders.list on the parent.
    """
    client = resourcemanager_v3.FoldersClient()
    folders = []
    for folder in client.list_folders(parent=parent):
        folders.append({
            "name": folder.name,
            "display_name": folder.display_name,
            "parent": folder.parent,
            "lifecycle_state": folder.state.name,
        })
    return folders


@mcp.tool()
def get_folder(folder_id: str) -> dict:
    """Get details of a specific GCP folder.

    Args:
        folder_id: Numeric folder ID (e.g. "41699456783") or full resource name
                   "folders/41699456783".

    Returns:
        Folder metadata: name, display_name, parent, lifecycle_state, create_time.
    Requires resourcemanager.folders.get on the folder.
    """
    if not folder_id.startswith("folders/"):
        folder_id = f"folders/{folder_id}"

    client = resourcemanager_v3.FoldersClient()
    folder = client.get_folder(name=folder_id)
    return {
        "name": folder.name,
        "display_name": folder.display_name,
        "parent": folder.parent,
        "lifecycle_state": folder.state.name,
        "create_time": str(folder.create_time),
        "update_time": str(folder.update_time),
    }


# ─── Projects ─────────────────────────────────────────────────────────────────

@mcp.tool()
def list_projects(parent: str) -> list[dict]:
    """List projects directly under an organization or a folder.

    Args:
        parent: Resource name of the parent. Examples:
                "organizations/123456789012"  ← top-level projects in the org
                "folders/41699456783"         ← projects inside a folder

    Returns:
        List of projects with project_id, name, display_name, and lifecycle_state.
    Requires resourcemanager.projects.list on the parent.
    """
    client = resourcemanager_v3.ProjectsClient()
    projects = []
    for project in client.list_projects(parent=parent):
        projects.append({
            "name": project.name,                    # "projects/..."
            "project_id": project.project_id,
            "display_name": project.display_name,
            "lifecycle_state": project.state.name,
            "labels": dict(project.labels),
        })
    return projects


@mcp.tool()
def search_projects(query: str) -> list[dict]:
    """Search for GCP projects across the entire organization using a query string.

    Args:
        query: Search query using Resource Manager filter syntax. Examples:
               ""                                         ← all accessible projects
               "parent:organizations/123456789012"        ← all projects in org
               "parent:folders/41699456783"              ← projects in a folder
               "labels.env=production"                    ← by label
               "lifecycleState:ACTIVE"                    ← only active projects
               "id:gcp-adk-demo*"                         ← wildcard project ID

    Returns:
        List of matching projects with project_id, display_name, and parent.
    """
    client = resourcemanager_v3.ProjectsClient()
    projects = []
    for project in client.search_projects(query=query):
        projects.append({
            "name": project.name,
            "project_id": project.project_id,
            "display_name": project.display_name,
            "lifecycle_state": project.state.name,
            "parent": project.parent,
            "labels": dict(project.labels),
        })
    return projects


@mcp.tool()
def get_project(project_id: str) -> dict:
    """Get detailed information about a specific GCP project.

    Args:
        project_id: The project ID (e.g. "gcp-adk-demo-123") or full resource
                    name "projects/gcp-adk-demo-123".

    Returns:
        Project metadata: project_id, display_name, parent, state, labels, create_time.
    Requires resourcemanager.projects.get on the project.
    """
    if not project_id.startswith("projects/"):
        project_id = f"projects/{project_id}"

    client = resourcemanager_v3.ProjectsClient()
    project = client.get_project(name=project_id)
    return {
        "name": project.name,
        "project_id": project.project_id,
        "display_name": project.display_name,
        "parent": project.parent,
        "lifecycle_state": project.state.name,
        "labels": dict(project.labels),
        "create_time": str(project.create_time),
        "update_time": str(project.update_time),
    }


@mcp.tool()
def get_project_iam_policy(project_id: str) -> dict:
    """Fetch the IAM policy attached to a GCP project.

    Args:
        project_id: The project ID (e.g. "gcp-adk-demo-123") or full resource
                    name "projects/gcp-adk-demo-123".

    Returns:
        Bindings list with role → members mappings.
    Requires resourcemanager.projects.getIamPolicy on the project.
    """
    if not project_id.startswith("projects/"):
        project_id = f"projects/{project_id}"

    client = resourcemanager_v3.ProjectsClient()
    request = iam_policy_pb2.GetIamPolicyRequest(resource=project_id)
    policy = client.get_iam_policy(request=request)

    bindings = []
    for b in policy.bindings:
        bindings.append({"role": b.role, "members": list(b.members)})
    return {"resource": project_id, "bindings": bindings, "etag": policy.etag.hex()}


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
