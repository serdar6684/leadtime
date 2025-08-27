#!/usr/bin/env bash
set -euo pipefail

pip-compile requirements.in
pip-compile requirements-dev.in