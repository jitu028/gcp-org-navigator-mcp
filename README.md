# GCP Org Navigator — ADK + MCP

An AI agent that lets you query your **GCP organization hierarchy** (organizations, folders, projects, IAM policies) in plain English — built with [Google Agent Development Kit (ADK)](https://adk.dev) and a custom [MCP](https://modelcontextprotocol.io) server backed by the Cloud Resource Manager API.

> 📖 Full walkthrough: [Medium article link]

---

## What it does

Ask the agent questions like:
- *"List all folders in my org"*
- *"Find all projects with label env=production"*
- *"What's the IAM policy on project my-project?"*
- *"Give me a full inventory of the org hierarchy"*

The agent automatically decides which tool to call, chains multiple calls if needed, and returns clean markdown tables.

---

## Architecture

```
User (browser)
      │ HTTP (ADK Dev UI)
ADK LlmAgent  ─── gemini-2.5-flash
      │ stdio (MCPToolset → child process)
FastMCP Server  (mcp_server.py)
      │ gRPC / REST (Application Default Credentials)
Cloud Resource Manager API
```

---

## MCP Tools

| Tool | Description |
|------|-------------|
| `list_organizations` | List all GCP orgs the caller has access to |
| `list_folders(parent)` | List folders under an org or folder |
| `get_folder(folder_id)` | Get details of a specific folder |
| `list_projects(parent)` | List projects under an org or folder |
| `search_projects(query)` | Org-wide project search with filter syntax |
| `get_project(project_id)` | Get details of a specific project |
| `get_org_iam_policy(org_id)` | Fetch IAM bindings on the org node |
| `get_project_iam_policy(project_id)` | Fetch IAM bindings on a project |

---

## Prerequisites

- Python 3.12+
- A GCP organization with `resourcemanager.organizations.search` permission
- `gcloud` CLI installed and authenticated

```bash
# Authenticate
gcloud auth application-default login

# Enable Vertex AI (for Gemini)
gcloud services enable aiplatform.googleapis.com --project=YOUR_PROJECT
```

---

## Setup

```bash
# Clone the repo
git clone https://github.com/jitu028/gcp-org-navigator-mcp.git
cd gcp-org-navigator-mcp

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your project ID
```

---

## Running

### Option A — Smoke test (no agent, validate API access)
```bash
python smoke_test.py
```

### Option B — ADK Web UI (chat interface)
```bash
adk web --port 8080
```
Open http://localhost:8080, select **`org_navigator`**, and start chatting.

---

## Configuration

Copy `.env.example` to `.env` and fill in your values:

```env
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
```

---

## Required IAM Permissions

The authenticated account needs these permissions at the **org level**:
- `resourcemanager.organizations.search`
- `resourcemanager.organizations.getIamPolicy` *(for org IAM policy tool)*
- `resourcemanager.folders.list` / `resourcemanager.folders.get`
- `resourcemanager.projects.list` / `resourcemanager.projects.get`
- `resourcemanager.projects.getIamPolicy` *(for project IAM policy tool)*

Predefined roles that cover these: `roles/resourcemanager.organizationViewer`, `roles/resourcemanager.folderViewer`

---

## Project Structure

```
.
├── __init__.py       ← ADK package registration (required)
├── agent.py          ← ADK LlmAgent wired to MCP via MCPToolset
├── mcp_server.py     ← FastMCP server exposing 8 Resource Manager tools
├── smoke_test.py     ← Direct tool test (no agent required)
├── requirements.txt  ← Python dependencies
├── .env.example      ← Environment variable template
└── README.md
```

---

## References

- [ADK Documentation](https://google.github.io/adk-docs/)
- [ADK MCP Tools](https://google.github.io/adk-docs/tools/mcp-tools/)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [Cloud Resource Manager API](https://cloud.google.com/resource-manager/docs/overview)
- [Resource Manager Python Client](https://cloud.google.com/python/docs/reference/resourcemanager/latest/google.cloud.resourcemanager_v3)
- [Application Default Credentials](https://cloud.google.com/docs/authentication/provide-credentials-adc)
- [Vertex AI Model Versions](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/model-versions)

---

## License

Apache 2.0
