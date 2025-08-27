"""Helper functions for standardised HTTP requests."""

from typing import Iterable, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import config


def get_retry_session(
    retries: int = config.RETRY_TOTAL,
    backoff_factor: int = config.RETRY_BACKOFF_FACTOR,
    status_forcelist: Optional[Iterable[int]] = None,
    allowed_methods: Optional[Iterable[str]] = None,
) -> requests.Session:
    """Create a requests session with retry logic."""
    retry_strategy = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=allowed_methods,
        raise_on_status=False,
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)

    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


__all__ = ["get_retry_session"]
