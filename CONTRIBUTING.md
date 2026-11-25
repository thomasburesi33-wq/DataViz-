# Travailler en groupe

L'historique du dépôt est consulté pour la notation : chacun commite **sous son propre compte**,
avec des messages clairs.

## Branches

- `main` : le socle commun (chargement, population, logique partagée, tableau de bord).
- `axe-1` … `axe-5` : une branche par axe, portée par son responsable, fusionnée par pull request.

```bash
git switch main && git pull
git switch -c axe-2                      # une fois
# ... travail sur analysis/axe_2.py et pages/2_Axe_2.py ...
git add analysis/axe_2.py pages/2_Axe_2.py DECISIONS.md
git commit -m "Axe 2 : part des langages par tranche d'âge"
git push -u origin axe-2                 # puis ouvrir une pull request vers main
```

Chaque axe a ses propres fichiers : les branches des axes ne se marchent pas dessus. Les fichiers
communs (`analysis/indicators.py`, `ui/common.py`, `ARCHITECTURE.md`, `DECISIONS.md`) se modifient
par petites pull requests relues par un autre membre.

## Avant chaque push

```bash
uv run pytest                            # la logique et les pages tournent toujours
```

## Règles

- Aucun `import streamlit` dans `analysis/` (un test le vérifie).
- Chaque figure affiche sa population avec `common.show_population`.
- Toute comparaison 2025 passe par `analysis/harmonisation.py` et est documentée dans
  `docs/harmonisation_2025_2026.md`.
- Une dépendance s'ajoute avec `uv add <paquet>` (met à jour `pyproject.toml` et `uv.lock`) ;
  commitez les deux fichiers.
- Jamais de données dans le dépôt.
