"""Common test fixtures."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))
import config
from tests.factories import FakeClient


@pytest.fixture(autouse=True)
def _pat_token(monkeypatch):
    """Ensure a PAT token is always set for tests."""
    monkeypatch.setattr(config, "PAT_TOKEN", "test-token")


@pytest.fixture
def fake_client():
    """Return a factory to build FakeClient instances."""
    def _factory(responses):
        return FakeClient(responses)
    return _factory
