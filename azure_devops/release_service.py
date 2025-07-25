"""Services to interact with Azure DevOps release resources."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from azure_devops.api_client import AzureDevOpsClient


def get_active_release_environments(
    client: AzureDevOpsClient, project_id: str, definition_id: int, top: int = 100
) -> List[Dict[str, Any]]:
    """Return data about succeeded release environments for active releases."""
    # pylint: disable=too-many-locals

    endpoint = f"/{project_id}/_apis/release/releases"
    params = {
        "api-version": client.api_version,
        "queryOrder": "descending",
        "$expand": "environments",
        "definitionId": definition_id,
        "$top": top,
    }

    releases = client.get(endpoint, params=params)
    results: List[Dict[str, Any]] = []

    for release in releases.get("value", []):
        if release.get("status") != "active":
            continue

        for environment in release.get("environments", []):
            if environment.get("status") not in {"succeeded", "partiallySucceeded"}:
                continue

            deploy_steps = environment.get("deploySteps", [])
            if not deploy_steps:
                continue

            queued_on = deploy_steps[0].get("queuedOn")
            last_modified = deploy_steps[0].get("lastModifiedOn")
            if not queued_on or not last_modified:
                continue

            start = datetime.fromisoformat(queued_on.replace("Z", "+00:00"))
            end = datetime.fromisoformat(last_modified.replace("Z", "+00:00"))
            duration = (end - start).total_seconds()

            results.append(
                {
                    "environment_id": environment.get("id"),
                    "release_id": environment.get("releaseId"),
                    "name": environment.get("name"),
                    "status": environment.get("status"),
                    "duration_seconds": duration,
                    "definition_environment_id": environment.get("definitionEnvironmentId"),
                }
            )

    return results
