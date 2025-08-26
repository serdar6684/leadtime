"""Service helpers related to Azure DevOps APIs."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import requests

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

def get_active_release_environments(
    client: AzureDevOpsClient, project_id: str, definition_id: int, top: int = 100
) -> List[Dict[str, Any]]:
    """Return all release environments where PRD was deployed successfully."""
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

            try:
                results.append(
                    {
                        "environment_id": environment.get("id"),
                        "environment_name": environment.get("name"),
                        "environment_status": environment.get("status"),
                        "environment_start_at": queued_on,
                        "environment_finished_at": last_modified,
                        "release_id": release.get("id"),
                        "release_name": release.get("name"),
                        "release_status": release.get("status"),
                        "release_created_on": release.get("createdOn"),
                        "release_modified_on": release.get("modifiedOn"),
                        "definition_environment_id": environment.get("definitionEnvironmentId"),
                    }
                )
            except KeyError as err:
                raise ValueError(
                    f"Erreur lors de l'extraction des informations de l'environment pour la release ID {release.get('id')}: {err}"
                ) from err

    return results

def get_all_artifact_metadata(
    client: AzureDevOpsClient, project_name: str, release_id: int
) -> List[Dict[str, str]]:
    """Extract all relevant metadata for each artifact in a given release."""
    endpoint = f"/{project_name}/_apis/release/releases/{release_id}"
    params = {"api-version": client.api_version}

    release_data = client.get(endpoint, params=params)
    artifacts = release_data.get("artifacts", [])

    if not artifacts:
        raise ValueError(f"Aucun artefact trouvé pour la release ID {release_id}.")
    
    results = []

    for artifact in artifacts:
        definition_ref = artifact.get("definitionReference", {})

        try:
            results.append(
                {
                    "alias": artifact.get("alias", "unknown"),
                    "branch_name": definition_ref["branch"]["name"],
                    "branch_id": definition_ref["branch"]["id"],
                    "repository_name": definition_ref["repository"]["name"],
                    "repository_id": definition_ref["repository"]["id"],
                    "definition_name": definition_ref["definition"]["name"],
                    "definition_id": definition_ref["definition"]["id"],
                    "commit_id": definition_ref["sourceVersion"]["id"],
                    "build_id": int(definition_ref["version"]["id"]),
                    "build_url": definition_ref["artifactSourceVersionUrl"]["id"],
                }
            )
        except KeyError as err:
            raise ValueError(
                f"Erreur lors de l'extraction des informations de l'artefact principal pour la release ID {release_id}: {err}"
            ) from err
    
    return results


def get_commit_date(
    client: AzureDevOpsClient, project_name: str, repository_id: str, commit_id: str
) -> Optional[str]:
    """Return the ISO timestamp of the given commit."""
    endpoint = f"/{project_name}/_apis/git/repositories/{repository_id}/commits/{commit_id}"
    params = {"api-version": client.api_version}

    try:
        response = client.get(endpoint, params=params)
        return response.get("committer", {}).get("date")
    except (requests.RequestException, ValueError, RuntimeError) as error:
        raise RuntimeError(
            f"Erreur lors de la récupération de la date du commit {commit_id}: {error}"
        ) from error


def find_pr_by_commit_id(
    client: AzureDevOpsClient,
    project_name: str,
    repository_id: str,
    commit_id: str,
    target_ref: str
) -> Optional[Dict[str, str]]:
    """
    Search for a completed PR whose merged commit matches the given commit_id.
    """
    endpoint = (
        f"/{project_name}/_apis/git/repositories/{repository_id}/pullRequests"
    )
    params = {
        "api-version": "7.1-preview.1",
        "searchCriteria.status": "completed",
        "searchCriteria.targetRefName": target_ref,
        "$top": 100
    }

    try:
        response = client.get(endpoint, params=params)
        for pr in response.get("value", []):
            merged_commit = pr.get("lastMergeCommit", {}).get("commitId")
            if merged_commit and merged_commit.lower() == commit_id.lower():
                return {
                    "id": str(pr["pullRequestId"]),
                    "merged_at": pr["closedDate"],
                    "created_at": pr["creationDate"],
                    "source_ref_name": pr["sourceRefName"],
                    "target_ref_name": pr["targetRefName"],
                    "status": pr["mergeStatus"],
                    "last_merge_commit_id": merged_commit,
                }
    except (
        requests.RequestException,
        ValueError,
        KeyError,
        RuntimeError,
    ) as error:
        raise RuntimeError(
            f"Erreur lors de la recherche de PR liée au commit : {error}"
        ) from error

    return None


def get_oldest_commit_from_pr(client, project_name, repo_id, pr_id):
    """Get the first commit in a given PR."""
    endpoint = f"/{project_name}/_apis/git/repositories/{repo_id}/pullRequests/{pr_id}/commits"
    params = {"api-version": "7.1-preview.1"}
    response = client.get(endpoint, params=params)

    commits = response.get("value", [])
    if not commits:
        return None

    # Le plus vieux commit est le premier de la liste
    return commits[-1].get("commitId"), commits[-1].get("committer", {}).get("date")
