"""Tests for azure_http helper functions."""

import requests

import config
from azure_http import get_retry_session


def test_get_retry_session_applies_configuration(monkeypatch):
    monkeypatch.setattr(config, "RETRY_TOTAL", 3)
    monkeypatch.setattr(config, "RETRY_BACKOFF_FACTOR", 1)

    session = get_retry_session(
        retries=config.RETRY_TOTAL,
        backoff_factor=config.RETRY_BACKOFF_FACTOR,
        status_forcelist=[500],
        allowed_methods=["GET"],
    )

    assert isinstance(session, requests.Session)
    adapter = session.get_adapter("http://")
    retries = adapter.max_retries
    assert retries.total == 3
    assert retries.backoff_factor == 1
    assert 500 in retries.status_forcelist
    assert "GET" in retries.allowed_methods