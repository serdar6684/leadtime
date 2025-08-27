"""Command line utility to fetch release environment metrics."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from azure_devops.ado_services import (find_pr_by_commit_id,
                                       get_active_release_environments,
                                       get_all_artifact_metadata,
                                       get_commit_date,
                                       get_oldest_commit_from_pr,
                                       get_project_id,
                                       get_release_definition_id)
from azure_devops.api_client import AzureDevOpsClient
from config import (API_VERSION, AZURE_ORG_URL, AZURE_RELEASE_URL, LOG_LEVEL,
                    PROJECT_NAME, STAGE_NAME)

logging.basicConfig(level=getattr(logging, LOG_LEVEL.upper(), logging.INFO))
logger = logging.getLogger(__name__)


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
        deployed_at = env.environment_finished_at
        if not deployed_at:
            continue

        try:
            artifacts = get_all_artifact_metadata(
                client_release, PROJECT_NAME, env.release_id
            )
        except ValueError as error:
            logger.warning("⚠️ Unable to read release artifacts : %s", error)
            continue

        for artifact in artifacts:
            commit_id = artifact.commit_id
            repo_id = artifact.repository_id

            commit_date = get_commit_date(client_core, PROJECT_NAME, repo_id, commit_id)

            if not commit_date:
                logger.warning(
                    "⚠️ Commit date not found for artifact %s (commit %s). Artifact ignored.",
                    artifact.alias,
                    commit_id,
                )
                continue

            metrics = {
                "lead_time_artifact_commit_to_prod": calculate_duration(
                    commit_date, deployed_at
                )
            }

            pr = find_pr_by_commit_id(
                client_core, PROJECT_NAME, repo_id, commit_id, artifact.branch_name
            )

            if pr:
                if pr.merged_at:
                    metrics["lead_time_pr_to_prod"] = calculate_duration(
                        pr.merged_at, deployed_at
                    )

                oldest_commit = get_oldest_commit_from_pr(
                    client_core, PROJECT_NAME, repo_id, pr.id
                )

                if not oldest_commit:
                    logger.warning(
                        "⚠️ No commit found for pull request %s linked to artifact %s. Artifact ignored.",
                        pr.id,
                        artifact.alias,
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
                    "id": env.release_id,
                    "name": env.release_name,
                    "status": env.release_status,
                    "created_on": env.release_created_on,
                    "modified_on": env.release_modified_on,
                    "definition": STAGE_NAME,
                    "deployed_at": deployed_at,
                },
                "environment": {
                    "id": env.environment_id,
                    "name": env.environment_name,
                    "status": env.environment_status,
                    "start_at": env.environment_start_at,
                    "finished_at": env.environment_finished_at,
                },
                "repository": {
                    "id": repo_id,
                    "name": artifact.repository_name,
                    "branch_name": artifact.branch_name,
                },
                "artifact": {
                    "alias": artifact.alias,
                    "branch_name": artifact.branch_name,
                    "branch_id": artifact.branch_id,
                    "commit_id": commit_id,
                    "commit_date": commit_date,
                    "build_id": artifact.build_id,
                    "build_url": artifact.build_url,
                },
                "pullrequest": {
                    "id": pr.id,
                    "merged_at": pr.merged_at,
                    "created_at": pr.created_at,
                    "source_ref_name": pr.source_ref_name,
                    "target_ref_name": pr.target_ref_name,
                    "status": pr.status,
                    "last_merge_commit_id": oldest_commit_id,
                    "last_merge_commit_date": oldest_commit_date,
                },
                "metrics": metrics,
            }

            # print(json.dumps(enriched_payload, indent=2))
            logger.info(json.dumps(enriched_payload, indent=2))


if __name__ == "__main__":
    main()
