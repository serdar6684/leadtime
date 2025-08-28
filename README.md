# Leadtime

## Overview

Leadtime is a command-line utility that gathers DORA lead time metrics from Azure DevOps releases.

The project uses [pip-tools](https://github.com/jazzband/pip-tools) to maintain pinned dependency files.

## Installation

### Prerequisites

- Python 3.10+
- `pip`

### Dependency Installation

```bash
pip install -r requirements.txt
```

## Configuration

Copy `example.env` to `.env` and fill in the required values
(Azure DevOps credentials, etc.):

```bash
cp example.env .env
# edit .env
```

## Usage

Run the application:

```bash
python main.py
```

## Tests

```bash
pytest
# or
make test
```

## Lint

```bash
pylint azure_http.py config.py main.py azure_devops
black --check .
bandit -r .
```

## Complete workflow

```bash
git clone <repository-url>
cd leadtime
pip install -r requirements.txt
cp example.env .env
# edit .env
python main.py
```

## Updating Dependencies

To regenerate `requirements.txt` and `requirements-dev.txt` from the `.in` files, run:

```bash
./scripts/lock.sh
```

This script uses [pip-tools](https://github.com/jazzband/pip-tools) to compile `requirements.in` and `requirements-dev.in` into their corresponding lock files.

## How to upgrade safely

1. Update the `.in` files or `pyproject.toml` with the new versions.
2. Run the lock script to regenerate the `.txt` files.
3. Run the test and lint suite (`pytest`, `pylint`, etc.).
4. Create a commit with the changes and the locked versions.

Use dedicated branches for upgrades and check major changelogs before applying updates.
