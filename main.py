"""Command line utility to fetch release environment metrics."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from azure_devops.api_client import AzureDevOpsClient
from azure_devops.ado_services import (
    get_project_id,
    get_release_definition_id,
    get_active_release_environments,
    get_all_artifact_metadata,
    get_commit_date,
    find_pr_by_commit_id,
    get_oldest_commit_from_pr
)
from config import (
    AZURE_ORG_URL,
    AZURE_RELEASE_URL,
    API_VERSION,
    PROJECT_NAME,
    STAGE_NAME,
)

def calculate_duration(from_date: str, to_date: str) -> dict:
    """Return a duration breakdown between two ISO timestamps."""
    start = datetime.fromisoformat(from_date.replace("Z", "+00:00"))
    end = datetime.fromisoformat(to_date.replace("Z", "+00:00"))

    delta = (end - start).total_seconds()
    return {
        "seconds": int(delta),
        "minutes": round(delta / 60, 2),
        "hours": round(delta / 3600, 2),
    }

def main() -> None:
    """Main entry point to collect and print DORA Lead Time metrics per artifact."""

    client_core = AzureDevOpsClient(AZURE_ORG_URL, API_VERSION)
    client_release = AzureDevOpsClient(AZURE_RELEASE_URL, API_VERSION)

    project_id = get_project_id(client_core, PROJECT_NAME)
    release_def_id = get_release_definition_id(client_release, project_id, STAGE_NAME)

    environments = get_active_release_environments(
        client_release, project_id, release_def_id
    )

    for env in environments:
        deployed_at = env.get("environment_finished_at")
        if not deployed_at:
            continue
        
        try:
            artifacts = get_all_artifact_metadata(
                client_release, PROJECT_NAME, env["release_id"]
            )
        except ValueError as error:
            print(f"⚠️ Impossible de lire les artefacts de la release : {error}")
            continue

        for artifact in artifacts:
            commit_id = artifact["commit_id"]
            repo_id = artifact["repository_id"]

            commit_date = get_commit_date(
                client_core, PROJECT_NAME, repo_id, commit_id
            )

            if not commit_date:
                print(
                    f"⚠️ Date de commit introuvable pour l'artefact {artifact['alias']} (commit {commit_id}). Artefact ignoré."
                )
                continue

            metrics = {
                "lead_time_artifact_commit_to_prod": calculate_duration(
                    commit_date, deployed_at
                )
            }

            pr = find_pr_by_commit_id(
                client_core, PROJECT_NAME, repo_id, commit_id, artifact["branch_name"]
            )

            if pr:
                if pr.get("merged_at"):
                    metrics["lead_time_pr_to_prod"] = calculate_duration(
                        pr["merged_at"], deployed_at
                    )
                
                oldest_commit = get_oldest_commit_from_pr(
                    client_core, PROJECT_NAME, repo_id, pr["id"]
                )

                if not oldest_commit:
                    print(
                        f"⚠️ Aucun commit trouvé pour la PR {pr['id']} liée à l'artefact {artifact['alias']}. Artefact ignoré."
                    )
                    continue
                oldest_commit_id, oldest_commit_date = oldest_commit
            else:
                continue

            metrics["lead_time_pr_last_commit_to_prod"] = calculate_duration(
                oldest_commit_date, deployed_at
            )

            enriched_payload = {
                "timestamp": datetime.now(tz=timezone.utc).isoformat(),
                "project": {
                    "name": PROJECT_NAME,
                    "id": project_id,
                },
                "release": {
                    "id": env["release_id"],
                    "name": env.get("release_name"),
                    "status": env.get("release_status"),
                    "created_on": env.get("release_created_on"),
                    "modified_on": env.get("release_modified_on"),
                    "definition": STAGE_NAME,
                    "deployed_at": deployed_at,
                },
                "environment": {
                    "id": env.get("environment_id"),
                    "name": env.get("environment_name"),
                    "status": env.get("environment_status"),
                    "start_at": env.get("environment_start_at"),
                    "finished_at": env.get("environment_finished_at"),
                },
                "repository": {
                    "id": repo_id,
                    "name": artifact["repository_name"],
                    "branch_name": artifact["branch_name"],
                },
                "artifact": {
                    "alias": artifact["alias"],
                    "branch_name": artifact["branch_name"],
                    "branch_id": artifact["branch_id"],
                    "commit_id": commit_id,
                    "commit_date": commit_date,
                    "build_id": artifact["build_id"],
                    "build_url": artifact["build_url"],
                },
                "pullrequest": {
                    "id": pr.get("id"),
                    "merged_at": pr.get("merged_at"),
                    "created_at": pr.get("created_at"),
                    "source_ref_name": pr.get("source_ref_name"),
                    "target_ref_name": pr.get("target_ref_name"),
                    "status": pr.get("status"),
                    "last_merge_commit_id": oldest_commit_id,
                    "last_merge_commit_date": oldest_commit_date,
                },
                "metrics": metrics,
            }

            print(json.dumps(enriched_payload, indent=2))


if __name__ == "__main__":
    main()
