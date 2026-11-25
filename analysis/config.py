"""Constantes partagées par toute l'application : chemins, sources, population par défaut.

Aucun import de Streamlit ici : ce module est lu par l'analyse, l'interface et les tests.
"""
import os
from pathlib import Path

# Racine du projet, quel que soit le dossier depuis lequel on lance les commandes.
ROOT = Path(__file__).resolve().parent.parent

# Dossier des données. Modifiable par la variable d'environnement SO_DATA_DIR
# (utile pour le déploiement ou pour partager un seul téléchargement entre plusieurs clones).
DATA_DIR = Path(os.environ.get("SO_DATA_DIR", ROOT / "data"))

_ARCHIVE = "https://media.githubusercontent.com/media/StackExchange/Survey/main/packages/archive"

# Les fichiers sont stockés avec Git LFS : on passe par media.githubusercontent.com,
# jamais par le lien « raw », qui ne renvoie qu'un pointeur de quelques octets.
SOURCES: dict[int, dict[str, str]] = {
    2026: {
        "results": f"{_ARCHIVE}/2026/survey_results_public.csv",
        "schema": f"{_ARCHIVE}/2026/survey_results_schema.csv",
    },
    2025: {
        "results": f"{_ARCHIVE}/2025/results.csv",
        "schema": f"{_ARCHIVE}/2025/schema.csv",
    },
}

MAIN_YEAR = 2026
COMPARISON_YEAR = 2025

# Taille minimale attendue de chaque fichier de réponses : en dessous, le téléchargement
# a échoué ou n'a récupéré qu'un pointeur Git LFS.
MIN_RESULTS_BYTES = 50_000_000


def results_path(year: int) -> Path:
    """Chemin local du fichier de réponses de l'année."""
    return DATA_DIR / f"survey_{year}_results.csv"


def schema_path(year: int) -> Path:
    """Chemin local du fichier de questions de l'année."""
    return DATA_DIR / f"survey_{year}_schema.csv"


# Population par défaut du tableau de bord : le marché du commanditaire.
# Une liste vide signifie « pas de filtre sur cette colonne » (convention du projet Olist).
DEFAULT_COUNTRIES = ["France"]
DEFAULT_CODE_MAIN: list[str] = []
DEFAULT_EMPLOYMENT: list[str] = []

# Effectif minimal sous lequel une part ou une médiane n'est pas affichée comme solide.
# Choix justifié dans DECISIONS.md.
MIN_N = 30

# Séparateur des questions à choix multiples (« Python;SQL;Rust »).
MULTI_SEP = ";"

SOURCE_LABEL = "Enquête Stack Overflow"
