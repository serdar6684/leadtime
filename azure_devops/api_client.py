"""HTTP client wrapper for Azure DevOps REST API."""

# pylint: disable=too-few-public-methods

from __future__ import annotations

import base64
from typing import Any, Dict, Optional
import requests
import config
from azure_http import get_retry_session

class AzureDevOpsClient:
    """Simple wrapper to perform authenticated HTTP requests."""

    def __init__(self, base_url: str, api_version: str) -> None:
        self.base_url = base_url
        self.api_version = api_version
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Configure an HTTP session with authentication headers."""

        if not config.PAT_TOKEN:
            raise ValueError("PAT_TOKEN is not set in the environment variables.")

        session = get_retry_session(
            retries=config.RETRY_TOTAL,
            backoff_factor=config.RETRY_BACKOFF_FACTOR,
        )
        pat_bytes = f":{config.PAT_TOKEN}".encode("utf-8")
        pat_token = base64.b64encode(pat_bytes).decode("utf-8")
        session.headers.update(
            {"Authorization": f"Basic {pat_token}", "Content-Type": "application/json"}
        )
        return session

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send a GET request and return the parsed JSON response.

        Applies the default timeout defined in :mod:`config` and raises a
        :class:`RuntimeError` if a network issue occurs.
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.get(
                url, params=params, timeout=config.DEFAULT_REQUEST_TIMEOUT,
            )
        except requests.RequestException as err:
            raise RuntimeError(
                f"Network error while requesting {url}: {err}"
            ) from err

        response.raise_for_status()
        return response.json()
