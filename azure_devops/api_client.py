"""HTTP client wrapper for Azure DevOps REST API."""

# pylint: disable=too-few-public-methods

from __future__ import annotations

import base64
from typing import Any, Dict, Optional

import requests

from config import PAT_TOKEN

class AzureDevOpsClient:
    """Simple wrapper to perform authenticated HTTP requests."""

    def __init__(self, base_url: str, api_version: str) -> None:
        self.base_url = base_url
        self.api_version = api_version
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Configure an HTTP session with authentication headers."""
        session = requests.Session()
        pat_bytes = f":{PAT_TOKEN}".encode("utf-8")
        pat_token = base64.b64encode(pat_bytes).decode("utf-8")
        session.headers.update(
            {"Authorization": f"Basic {pat_token}", "Content-Type": "application/json"}
        )
        return session

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send a GET request and return the parsed JSON response."""
        url = f"{self.base_url}{endpoint}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()
