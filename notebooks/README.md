# Notebooks d'exploration

- `00_prise_en_main.ipynb` : chargement, schéma des questions, population France.
- Un notebook par axe : `0N_axe_N_<prénom>.ipynb`. Ce qui est retenu passe ensuite dans
  `analysis/axe_N.py`, pour être testé et affiché par l'application.

Avant de commiter un notebook, videz ses sorties (Kernel → Restart & Clear Outputs) : le dépôt reste
léger et ne contient aucune donnée.

```bash
uv sync --group notebooks
uv run jupyter lab
```
