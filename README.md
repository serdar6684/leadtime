# Leadtime

## Présentation

The project uses [pip-tools](https://github.com/jazzband/pip-tools) to maintain pinned dependency files.
Leadtime est un utilitaire en ligne de commande permettant de collecter les
indicateurs de délai DORA à partir des releases Azure DevOps.

The project uses [pip-tools](https://github.com/jazzband/pip-tools) to maintain pinned dependency files.

## Installation

### Prérequis

- Python 3.10+
- `pip`

### Installation des dépendances

```bash
pip install -r requirements.txt
```

## Configuration

Copiez `example.env` vers `.env` puis renseignez les valeurs nécessaires
(identifiants Azure DevOps, etc.) :

```bash
cp example.env .env
# éditer .env
```

## Utilisation

Exécuter l'application :

```bash
python main.py
```

## Tests

```bash
pytest
# ou
make test
```

## Lint

```bash
pylint azure_http.py config.py main.py azure_devops
black --check .
bandit -r .
```

## Workflow complet

```bash
git clone <URL-du-dépôt>
cd leadtime
pip install -r requirements.txt
cp example.env .env
# éditer .env
python main.py
```

## Mise à jour des dépendances

Le projet utilise [pip-tools](https://github.com/jazzband/pip-tools) pour
verrouiller les dépendances. Pour régénérer `requirements.txt` et
`requirements-dev.txt` à partir des fichiers `.in` :

```bash
./scripts/lock.sh
```

This script compiles `requirements.in` and `requirements-dev.in` into their corresponding lock files.

## How to upgrade safely

1. Mettre à jour les fichiers `.in` ou `pyproject.toml` avec les nouvelles versions.
2. Lancer le script de lock pour régénérer les fichiers `.txt`.
3. Exécuter la suite de tests et de lint (`pytest`, `pylint`, etc.).
4. Créer un commit avec les modifications et les versions verrouillées.

Utilisez des branches dédiées pour les mises à niveau et vérifiez les changelogs majeurs avant d'appliquer les mises à jour.