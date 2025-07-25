"""Service helpers related to Azure DevOps projects."""

from __future__ import annotations

from azure_devops.api_client import AzureDevOpsClient

def get_project_id(client: AzureDevOpsClient, project_name: str) -> str:
    """Return the project identifier for the given project name."""

    endpoint = "/_apis/projects"
    params = {"api-version": client.api_version}
    data = client.get(endpoint, params=params)

    for project in data.get("value", []):
        if project.get("name") == project_name:
            return project.get("id")

    raise ValueError(f"Projet nommé '{project_name}' introuvable.")
