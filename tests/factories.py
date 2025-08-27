"""Test factories for data models and fake clients."""

from __future__ import annotations

from typing import Any, Dict, Tuple

from azure_devops.models import Artifact, PullRequest, ReleaseEnvironment


class FakeClient:
    """Simple fake AzureDevOpsClient returning pre-defined responses."""

    def __init__(self, responses: Dict[Tuple[str, Tuple[Tuple[str, Any], ...]], Any], api_version: str = "7.1") -> None:
        self.api_version = api_version
        self._responses = responses

    def get(self, endpoint: str, params: Dict[str, Any] | None = None) -> Any:
        key = (endpoint, tuple(sorted((params or {}).items())))
        result = self._responses.get(key)
        if isinstance(result, Exception):
            raise result
        return result


def build_release_environment(**overrides: Any) -> ReleaseEnvironment:
    data = {
        "environment_id": 1,
        "environment_name": "Prod",
        "environment_status": "succeeded",
        "environment_start_at": "2021-01-01T00:00:00Z",
        "environment_finished_at": "2021-01-01T01:00:00Z",
        "release_id": 1,
        "release_name": "Release1",
        "release_status": "active",
        "release_created_on": "2021-01-01T00:00:00Z",
        "release_modified_on": "2021-01-01T00:30:00Z",
        "definition_environment_id": 10,
    }
    data.update(overrides)
    return ReleaseEnvironment(**data)


def build_artifact(**overrides: Any) -> Artifact:
    data = {
        "alias": "artifact",
        "branch_name": "main",
        "branch_id": "1",
        "repository_name": "repo",
        "repository_id": "2",
        "definition_name": "def",
        "definition_id": "3",
        "commit_id": "c1",
        "build_id": 4,
        "build_url": "http://example.com",
    }
    data.update(overrides)
    return Artifact(**data)


def build_pull_request(**overrides: Any) -> PullRequest:
    data = {
        "id": "1",
        "merged_at": "2021-01-01T00:00:00Z",
        "created_at": "2020-12-31T23:00:00Z",
        "source_ref_name": "feature",
        "target_ref_name": "main",
        "status": "succeeded",
        "last_merge_commit_id": "abc",
    }
    data.update(overrides)
    return PullRequest(**data)
