"""Data models used by the Azure DevOps service helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class ReleaseEnvironment:
    """A deployment environment for a given release."""

    environment_id: int
    environment_name: str
    environment_status: str
    environment_start_at: str
    environment_finished_at: str
    release_id: int
    release_name: str
    release_status: str
    release_created_on: str
    release_modified_on: str
    definition_environment_id: int


@dataclass
class Artifact:
    """Metadata describing an artifact deployed in a release."""

    alias: str
    branch_name: str
    branch_id: str
    repository_name: str
    repository_id: str
    definition_name: str
    definition_id: str
    commit_id: str
    build_id: int
    build_url: str


@dataclass
class PullRequest:
    """Essential information about a pull request."""

    id: str
    merged_at: Optional[str]
    created_at: Optional[str]
    source_ref_name: str
    target_ref_name: str
    status: str
    last_merge_commit_id: str


__all__ = [
    "ReleaseEnvironment",
    "Artifact",
    "PullRequest",
]
