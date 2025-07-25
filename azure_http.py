"""Helper functions to standardize HTTP responses in Azure Functions."""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import config

def get_retry_session() -> requests.Session:
    """Create a requests session with retry logic."""
    retry_strategy = Retry(
        total=config.RETRY_TOTAL,
        backoff_factor=config.RETRY_BACKOFF_FACTOR,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        raise_on_status=False,
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)

    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session
