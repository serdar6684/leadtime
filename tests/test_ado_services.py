"""Tests for Azure DevOps service helpers."""
"""Tests for Azure DevOps service helpers."""

import pytest
import requests

from azure_devops import ado_services
from tests.factories import build_release_environment


def _key(endpoint: str, params: dict[str, object]) -> tuple[str, tuple[tuple[str, object], ...]]:
    return endpoint, tuple(sorted(params.items()))


def test_get_project_id_found(fake_client):
    params = {"api-version": "7.1"}
    responses = {_key("/_apis/projects", params): {"value": [{"name": "One", "id": "123"}]}}
    client = fake_client(responses)
    assert ado_services.get_project_id(client, "One") == "123"


def test_get_project_id_not_found(fake_client):
    params = {"api-version": "7.1"}
    responses = {_key("/_apis/projects", params): {"value": []}}
    client = fake_client(responses)
    with pytest.raises(ValueError):
        ado_services.get_project_id(client, "Missing")


def test_get_release_definition_id(fake_client):
    params = {"api-version": "7.1", "searchText": "def"}
    responses = {_key("/proj/_apis/release/definitions", params): {"value": [{"name": "def", "id": 7}]}}
    client = fake_client(responses)
    assert ado_services.get_release_definition_id(client, "proj", "def") == 7


def test_get_release_definition_id_not_found(fake_client):
    params = {"api-version": "7.1", "searchText": "def"}
    responses = {_key("/proj/_apis/release/definitions", params): {"value": []}}
    client = fake_client(responses)
    with pytest.raises(ValueError):
        ado_services.get_release_definition_id(client, "proj", "def")


def test_get_active_release_environments(fake_client):
    params = {
        "api-version": "7.1",
        "queryOrder": "descending",
        "$expand": "environments",
        "definitionId": 2,
        "$top": 100,
    }
    responses = {
        _key("/p/_apis/release/releases", params): {
            "value": [
                {
                    "id": 1,
                    "name": "r1",
                    "status": "active",
                    "createdOn": "2021-01-01T00:00:00Z",
                    "modifiedOn": "2021-01-01T00:30:00Z",
                    "environments": [
                        {
                            "id": 11,
                            "name": "Prod",
                            "status": "succeeded",
                            "deploySteps": [
                                {
                                    "queuedOn": "2021-01-01T00:00:00Z",
                                    "lastModifiedOn": "2021-01-01T01:00:00Z",
                                }
                            ],
                            "definitionEnvironmentId": 10,
                        }
                    ],
                },
                {"id": 2, "status": "abandoned"},
            ]
        }
    }
    client = fake_client(responses)
    envs = ado_services.get_active_release_environments(client, "p", 2)
    assert len(envs) == 1
    assert isinstance(envs[0], type(build_release_environment()))


def test_get_active_release_environments_failed_status(fake_client):
    params = {
        "api-version": "7.1",
        "queryOrder": "descending",
        "$expand": "environments",
        "definitionId": 2,
        "$top": 100,
    }
    responses = {
        _key("/p/_apis/release/releases", params): {
            "value": [
                {
                    "id": 1,
                    "name": "r1",
                    "status": "active",
                    "createdOn": "2021-01-01T00:00:00Z",
                    "modifiedOn": "2021-01-01T00:30:00Z",
                    "environments": [
                        {
                            "id": 11,
                            "name": "Prod",
                            "status": "failed",
                            "deploySteps": [
                                {
                                    "queuedOn": "2021-01-01T00:00:00Z",
                                    "lastModifiedOn": "2021-01-01T01:00:00Z",
                                }
                            ],
                            "definitionEnvironmentId": 10,
                        }
                    ],
                },
                {"id": 2, "status": "abandoned"},
            ]
        }
    }
    client = fake_client(responses)
    envs = ado_services.get_active_release_environments(client, "p", 2)
    assert len(envs) == 0


def test_get_active_release_environments_without_deploysteps(fake_client):
    params = {
        "api-version": "7.1",
        "queryOrder": "descending",
        "$expand": "environments",
        "definitionId": 2,
        "$top": 100,
    }
    responses = {
        _key("/p/_apis/release/releases", params): {
            "value": [
                {
                    "id": 1,
                    "name": "r1",
                    "status": "active",
                    "createdOn": "2021-01-01T00:00:00Z",
                    "modifiedOn": "2021-01-01T00:30:00Z",
                    "environments": [
                        {
                            "id": 11,
                            "name": "Prod",
                            "status": "succeeded",
                            "deploySteps": [],
                            "definitionEnvironmentId": 10,
                        }
                    ],
                },
                {"id": 2, "status": "abandoned"},
            ]
        }
    }
    client = fake_client(responses)
    envs = ado_services.get_active_release_environments(client, "p", 2)
    assert len(envs) == 0


def test_get_active_release_environments_without_queuedOn(fake_client):
    params = {
        "api-version": "7.1",
        "queryOrder": "descending",
        "$expand": "environments",
        "definitionId": 2,
        "$top": 100,
    }
    responses = {
        _key("/p/_apis/release/releases", params): {
            "value": [
                {
                    "id": 1,
                    "name": "r1",
                    "status": "active",
                    "createdOn": "2021-01-01T00:00:00Z",
                    "modifiedOn": "2021-01-01T00:30:00Z",
                    "environments": [
                        {
                            "id": 11,
                            "name": "Prod",
                            "status": "succeeded",
                            "deploySteps": [
                                {
                                    "lastModifiedOn": "2021-01-01T01:00:00Z",
                                }
                            ],
                            "definitionEnvironmentId": 10,
                        }
                    ],
                },
                {"id": 2, "status": "abandoned"},
            ]
        }
    }
    client = fake_client(responses)
    envs = ado_services.get_active_release_environments(client, "p", 2)
    assert len(envs) == 0


def test_get_all_artifact_metadata(fake_client):
    endpoint = "/proj/_apis/release/releases/1"
    params = {"api-version": "7.1"}
    responses = {
        _key(endpoint, params): {
            "artifacts": [
                {
                    "alias": "a",
                    "definitionReference": {
                        "branch": {"name": "main", "id": "1"},
                        "repository": {"name": "repo", "id": "2"},
                        "definition": {"name": "def", "id": "3"},
                        "sourceVersion": {"id": "c1"},
                        "version": {"id": "4"},
                        "artifactSourceVersionUrl": {"id": "url"},
                    },
                }
            ]
        }
    }
    client = fake_client(responses)
    artifacts = ado_services.get_all_artifact_metadata(client, "proj", 1)
    assert artifacts[0].alias == "a"


def test_get_all_artifact_metadata_no_artifact(fake_client):
    endpoint = "/proj/_apis/release/releases/1"
    params = {"api-version": "7.1"}
    responses = {_key(endpoint, params): {"artifacts": []}}
    client = fake_client(responses)
    with pytest.raises(ValueError):
        ado_services.get_all_artifact_metadata(client, "proj", 1)


def test_get_all_artifact_metadata_malformed(fake_client):
    endpoint = "/proj/_apis/release/releases/1"
    params = {"api-version": "7.1"}
    responses = {
        _key(endpoint, params): {"artifacts": [{"alias": "a", "definitionReference": {}}]}
    }
    client = fake_client(responses)
    with pytest.raises(ValueError):
        ado_services.get_all_artifact_metadata(client, "proj", 1)


def test_get_commit_date(fake_client):
    endpoint = "/proj/_apis/git/repositories/repo/commits/abc"
    params = {"api-version": "7.1"}
    responses = {
        _key(endpoint, params): {"committer": {"date": "2021-01-01T00:00:00Z"}}
    }
    client = fake_client(responses)
    assert ado_services.get_commit_date(client, "proj", "repo", "abc") == "2021-01-01T00:00:00Z"


def test_get_commit_date_error(fake_client):
    endpoint = "/proj/_apis/git/repositories/repo/commits/abc"
    params = {"api-version": "7.1"}
    responses = {_key(endpoint, params): requests.RequestException("boom")}
    client = fake_client(responses)
    with pytest.raises(RuntimeError):
        ado_services.get_commit_date(client, "proj", "repo", "abc")


def test_find_pr_by_commit_id(fake_client):
    endpoint = "/proj/_apis/git/repositories/repo/pullRequests"
    params = {
        "api-version": "7.1-preview.1",
        "searchCriteria.status": "completed",
        "searchCriteria.targetRefName": "main",
        "$top": 100,
    }
    responses = {
        _key(endpoint, params): {
            "value": [
                {
                    "pullRequestId": 1,
                    "lastMergeCommit": {"commitId": "abc"},
                    "closedDate": "2021-01-02T00:00:00Z",
                    "creationDate": "2021-01-01T00:00:00Z",
                    "sourceRefName": "feature",
                    "targetRefName": "main",
                    "mergeStatus": "completed",
                }
            ]
        }
    }
    client = fake_client(responses)
    pr = ado_services.find_pr_by_commit_id(client, "proj", "repo", "abc", "main")
    assert pr and pr.id == "1"


def test_find_pr_by_commit_id_none(fake_client):
    endpoint = "/proj/_apis/git/repositories/repo/pullRequests"
    params = {
        "api-version": "7.1-preview.1",
        "searchCriteria.status": "completed",
        "searchCriteria.targetRefName": "main",
        "$top": 100,
    }
    responses = {_key(endpoint, params): {"value": []}}
    client = fake_client(responses)
    assert ado_services.find_pr_by_commit_id(client, "proj", "repo", "abc", "main") is None


def test_find_pr_by_commit_id_error(fake_client):
    endpoint = "/proj/_apis/git/repositories/repo/pullRequests"
    params = {
        "api-version": "7.1-preview.1",
        "searchCriteria.status": "completed",
        "searchCriteria.targetRefName": "main",
        "$top": 100,
    }
    responses = {_key(endpoint, params): requests.RequestException("boom")}
    client = fake_client(responses)
    with pytest.raises(RuntimeError):
        ado_services.find_pr_by_commit_id(client, "proj", "repo", "abc", "main")


def test_get_oldest_commit_from_pr(fake_client):
    endpoint = "/proj/_apis/git/repositories/repo/pullRequests/1/commits"
    params = {"api-version": "7.1-preview.1"}
    responses = {
        _key(endpoint, params): {
            "value": [
                {"commitId": "c1", "committer": {"date": "2021-01-01"}},
                {"commitId": "c0", "committer": {"date": "2020-12-31"}},
            ]
        }
    }
    client = fake_client(responses)
    commit_id, commit_date = ado_services.get_oldest_commit_from_pr(client, "proj", "repo", "1")
    assert commit_id == "c0"
    assert commit_date == "2020-12-31"


def test_get_oldest_commit_from_pr_empty(fake_client):
    endpoint = "/proj/_apis/git/repositories/repo/pullRequests/1/commits"
    params = {"api-version": "7.1-preview.1"}
    responses = {_key(endpoint, params): {"value": []}}
    client = fake_client(responses)
    assert ado_services.get_oldest_commit_from_pr(client, "proj", "repo", "1") is None
