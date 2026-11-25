# Architecture technique

Premier document lu par le jury : il permet de suivre les données du fichier brut jusqu'à chaque
figure. **À tenir à jour à chaque fusion d'un axe.**

## Principe : l'analyse est séparée de l'interface

```
analysis/   fonctions pures (pandas)        → aucune ligne n'importe Streamlit (vérifié par un test)
ui/         briques Streamlit + figures     → ne calcule rien, reçoit des tables
app.py      tableau de bord principal       → présentation uniquement
pages/      un fichier par axe              → présentation uniquement
```

Chaque figure repose sur une table renvoyée par une fonction d'`analysis/`, testable sans interface.

## Fonctionnalités principales

| Fonctionnalité | Fichiers | Fonctions |
| --- | --- | --- |
| Téléchargement des données | `get_data.py`, `analysis/load.py` | `ensure_data`, `_download` |
| Chargement des réponses | `analysis/load.py` | `load_survey`, `load_schema`, `question_text` |
| Filtres de population communs | `analysis/population.py`, `ui/common.py` | `filter_population`, `population_filters` |
| Population affichée sous chaque figure | `analysis/population.py`, `ui/common.py` | `describe_population`, `population_caption`, `show_population` |
| Indicateurs partagés | `analysis/indicators.py` | `share_single`, `share_multi`, `median_by`, `headline_kpis` |
| Tableau de bord principal | `app.py` | — |
| Axe *n* (×5) | `analysis/axe_n.py`, `pages/n_Axe_n.py` | `filter_axis`, `main_table` |
| Comparaison 2025 | `analysis/harmonisation.py`, `ui/common.py` | `harmonise_2025`, `comparable`, `load_2025_harmonised` |
| Figures | `ui/charts.py` | `barh_shares`, `barh_medians` |

## Circulation des données

```
StackExchange/Survey (GitHub, Git LFS)
   │  get_data.py → analysis.load.ensure_data        (téléchargement atomique, contrôle de taille)
   ▼
data/survey_2026_results.csv  (+ survey_2025_results.csv en option)
   │  analysis.load.load_survey                       (lecture, conversion des colonnes numériques)
   │  ui.common.load_year            [cache]          (une seule lecture pour toutes les pages)
   ▼
DataFrame complet 2026 (30 903 répondants × 212 colonnes)
   │  ui.common.population_filters → analysis.population.filter_population
   ▼
Population (par défaut : France)
   │  analysis.axe_n.filter_axis                      (filtres propres à l'axe)
   ▼
Sélection
   │  analysis.indicators.* / analysis.axe_n.main_table
   ▼
Table de la figure ──► ui.charts.* ──► st.pyplot          + ui.common.show_population (qui, année, n)
```

Comparaison 2025 : `load_survey(2025)` → `harmonisation.harmonise_2025` (colonnes renommées et
recodées) → cache `load_2025_harmonised` → `harmonisation.comparable` (empile les deux années).

## Cache

| Fonction | Décorateur | Pourquoi |
| --- | --- | --- |
| `ui.common.load_year(year)` | `@st.cache_data` | Lire 120 Mo à chaque interaction rendrait l'app inutilisable |
| `ui.common.load_2025_harmonised()` | `@st.cache_data` | Idem ; seule la version harmonisée (quelques colonnes) est gardée |
| `ui.common.load_schema(year)` | `@st.cache_data` | Petit fichier relu par plusieurs pages |

Les filtres et les indicateurs ne sont **pas** mis en cache : ils prennent quelques millisecondes,
le cache coûterait plus cher que le calcul. Les DataFrames renvoyés par le cache ne sont jamais
modifiés en place (`.assign()` ou `.copy()`).

## Données de session

| Clé | Contenu | Portée |
| --- | --- | --- |
| `pop_countries`, `pop_code_main`, `pop_employment` | Filtres de population choisis | Toutes les pages : conservés quand on change de page |
| `_w_pop_*` | Clés des widgets correspondants, recopiées depuis `pop_*` à chaque affichage | Technique |
| `axeN_*` | Filtres propres à l'axe *N* | Page de l'axe uniquement |

Streamlit efface l'état d'un widget quand on quitte la page où il est affiché : la valeur est donc
gardée sous une clé permanente (`pop_*`) et recopiée dans la clé du widget (`_w_pop_*`).
