"""Command line utility to fetch release environment metrics."""

from __future__ import annotations

from azure_devops.api_client import AzureDevOpsClient
from azure_devops.project_service import get_project_id
from azure_devops.release_definition_service import get_release_definition_id
from azure_devops.release_service import get_active_release_environments
from config import (
    AZURE_ORG_URL,
    AZURE_RELEASE_URL,
    API_VERSION,
    PROJECT_NAME,
    STAGE_NAME,
)

def main() -> None:
    """Retrieve project and release information then display metrics."""

    client_core = AzureDevOpsClient(AZURE_ORG_URL, API_VERSION)
    client_release = AzureDevOpsClient(AZURE_RELEASE_URL, API_VERSION)

    project_id = get_project_id(client_core, PROJECT_NAME)
    release_def_id = get_release_definition_id(
        client_release, project_id, STAGE_NAME
    )

    environments = get_active_release_environments(
        client_release, project_id, release_def_id
    )
    for env in environments:
        print(env)

if __name__ == "__main__":
    main()
