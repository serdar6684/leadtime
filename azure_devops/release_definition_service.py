"""Services related to Azure DevOps release definitions."""

from __future__ import annotations

from azure_devops.api_client import AzureDevOpsClient

def get_release_definition_id(
    client: AzureDevOpsClient, project_id: str, definition_name: str
) -> int:
    """Return the release definition identifier matching the given name."""
    endpoint = (
        f"/{project_id}/_apis/release/definitions"
    )
    params = {
        "api-version": client.api_version,
        "searchText": definition_name
    }

    data = client.get(endpoint, params=params)
    definitions = data.get("value", [])

    for definition in definitions:
        if definition.get("name") == definition_name:
            return definition.get("id")

    raise ValueError(f"Release definition '{definition_name}' introuvable.")
