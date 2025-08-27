"""
This module centralizes application-wide configurations and constants.
It includes settings for retry logic, environment variable defaults,
and other global parameters used throughout the project.
"""

import os

from dotenv import load_dotenv

load_dotenv()

AZURE_ORG_URL = "https://dev.azure.com/lpl-sources"
AZURE_RELEASE_URL = "https://vsrm.dev.azure.com/lpl-sources"
API_VERSION = "7.1"
PAT_TOKEN = os.getenv("PAT_TOKEN")

# HTTP Client
DEFAULT_REQUEST_TIMEOUT = 10
RETRY_TOTAL = 5
RETRY_BACKOFF_FACTOR = 2

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Project information
PROJECT_NAME = "One"
STAGE_NAME = "ONE-2205-AMER-OAT/PRD"
