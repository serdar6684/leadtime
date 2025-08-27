# Leadtime

## Dependency locking

The project uses [pip-tools](https://github.com/jazzband/pip-tools) to maintain pinned dependency files.

To update `requirements.txt` and `requirements-dev.txt`, run:

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