# Application d'analyse — enquête Stack Overflow 2026

Projet final du cours **ECE : Data Visualisation**, mené par Nathan Rullaud, Jean-Christophe Chalaud,
Baptiste Lemaître et Thomas Buresi.

Une application Streamlit pour un commanditaire du marché français : un tableau de bord principal
porteur d'un message, et cinq axes d'approfondissement, chacun avec ses filtres et ses vues.
Thème, commanditaire et message : voir [`CADRAGE.md`](CADRAGE.md).

## Lancer l'application depuis un clone frais

Seul prérequis : [uv](https://docs.astral.sh/uv/getting-started/installation/), qui installe
lui-même la bonne version de Python.

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Puis, sur toutes les machines :

```bash
git clone https://github.com/thomasburesi33-wq/DataViz-.git
cd DataViz-
uv sync                                  # crée .venv avec les versions épinglées (uv.lock)
uv run python get_data.py                # télécharge l'enquête 2026 dans data/ (~120 Mo, une fois)
uv run streamlit run app.py              # ouvre http://localhost:8501
```

Options :

```bash
uv run python get_data.py --with-2025    # ajoute l'enquête 2025 pour les comparaisons (~140 Mo)
uv run pytest                            # tests de la logique (+ des pages si les données sont là)
uv sync --group notebooks                # installe Jupyter pour les notebooks d'exploration
uv run jupyter lab
```

Si `get_data.py` n'a pas été lancé, l'application télécharge les données toute seule au premier
démarrage. Les données ne sont **jamais** versionnées (`data/` est ignoré par Git).

## Organisation du dépôt

| Chemin | Rôle |
| --- | --- |
| `app.py` | Tableau de bord principal : le message pour le commanditaire |
| `pages/1_Axe_1.py` … `pages/5_Axe_5.py` | Les cinq axes : présentation uniquement |
| `analysis/` | Toute l'analyse, sans Streamlit : chargement, population, indicateurs, harmonisation, un module par axe |
| `ui/common.py` | Briques d'interface partagées : cache, filtres de population, données de session |
| `ui/charts.py` | Figures matplotlib construites à partir des tables d'`analysis` |
| `get_data.py` | Téléchargement des données |
| `notebooks/` | Notebooks d'exploration |
| `tests/` | Tests de la logique et des pages |
| `ARCHITECTURE.md` | Architecture technique : fonctionnalités, fichiers, flux de données, cache, session |
| `DECISIONS.md` | Choix de conception et leurs raisons |
| `docs/harmonisation_2025_2026.md` | Correspondances entre les questions 2025 et 2026 |
| `CONTRIBUTING.md` | Organisation du travail en groupe sur Git |

## Données

[Enquête Stack Overflow](https://survey.stackoverflow.co/2026), archive officielle
[StackExchange/Survey](https://github.com/StackExchange/Survey) (`packages/archive/2026`, et `2025`
en option). Les répondants sont des volontaires ayant répondu à une enquête en ligne : les parts
affichées décrivent ces répondants, pas l'ensemble des développeurs.
