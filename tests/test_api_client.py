"""Tests for AzureDevOpsClient."""

import base64
import requests
import pytest

from azure_devops.api_client import AzureDevOpsClient
import config


def test_missing_pat_token_raises(monkeypatch):
    monkeypatch.setattr(config, "PAT_TOKEN", "")
    with pytest.raises(ValueError):
        AzureDevOpsClient("http://example.com", "1.0")


def test_session_has_auth_header(monkeypatch):
    monkeypatch.setattr(config, "PAT_TOKEN", "abc")
    client = AzureDevOpsClient("http://example.com", "1.0")
    auth = client.session.headers["Authorization"].split()[1]
    assert base64.b64decode(auth).decode() == ":abc"


def test_get_success(monkeypatch, requests_mock):
    monkeypatch.setattr(config, "PAT_TOKEN", "abc")
    client = AzureDevOpsClient("http://example.com", "1.0")
    requests_mock.get("http://example.com/test", json={"ok": True})
    assert client.get("/test") == {"ok": True}


def test_get_network_error(monkeypatch):
    monkeypatch.setattr(config, "PAT_TOKEN", "abc")
    client = AzureDevOpsClient("http://example.com", "1.0")

    def boom(*_, **__):
        raise requests.RequestException("boom")

    monkeypatch.setattr(client.session, "get", boom)
    with pytest.raises(RuntimeError):
        client.get("/test")
