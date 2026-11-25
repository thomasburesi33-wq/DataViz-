"""Harmonisation des réponses 2025 sur le référentiel 2026.

Toute comparaison entre les deux années passe par `harmonise_2025` : aucune page ne compare
directement une colonne 2025 à une colonne 2026. Chaque correspondance ci-dessous est
justifiée dans docs/harmonisation_2025_2026.md ; ajoutez-y une ligne à chaque ajout ici.
"""
from __future__ import annotations

import pandas as pd

from analysis import config

# Colonne 2025 -> colonne 2026, uniquement quand la question ET ses modalités sont
# comparables (vérifié dans docs/harmonisation_2025_2026.md).
COLUMN_MAP: dict[str, str] = {
    "Country": "Country",
    "Age": "Age",
    "Employment": "Employment",
    "OrgSize": "OrgSize",
    "RemoteWork": "WorkSetting",          # renommée en 2026, modalités identiques
    "JobSat": "JobSat",
    "WorkExp": "WorkExp",
    "ConvertedCompYearly": "ConvertedCompYearly",
    "LanguageHaveWorkedWith": "LanguagesHaveWorkedWith",  # choix multiples, renommée
}

# Recodage de modalités, par colonne 2026 : {modalité d'origine: modalité commune}.
# Vide tant qu'aucune modalité n'a besoin d'être recodée.
VALUE_MAPS: dict[str, dict[str, str]] = {}

# Modalités présentes une seule année, à exclure avant toute comparaison,
# par colonne 2026. Exemple : la tranche « Under 18 » n'existe qu'en 2026.
EXCLUDE_VALUES: dict[str, set[str]] = {
    "Age": {"Under 18 years old"},
}

# Colonnes au même nom mais à la question différente : ne JAMAIS comparer telles quelles.
# AISelect est une question à choix unique en 2025 (« utilisez-vous l'IA ? ») et une question
# à choix multiples sur les types d'outils en 2026.
NOT_COMPARABLE = {"AISelect", "ICorPM"}


def harmonise_2025(df_2025: pd.DataFrame) -> pd.DataFrame:
    """Renvoie les réponses 2025 restreintes aux colonnes comparables, renommées et recodées
    selon le référentiel 2026, avec la colonne `year`."""
    keep = [c for c in COLUMN_MAP if c in df_2025.columns]
    out = df_2025[keep].rename(columns=COLUMN_MAP)
    for col, mapping in VALUE_MAPS.items():
        if col in out.columns:
            out[col] = out[col].replace(mapping)
    for col in ("WorkExp", "ConvertedCompYearly"):
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    return out.assign(year=config.COMPARISON_YEAR)


def comparable(df_2026: pd.DataFrame, df_2025_harmonised: pd.DataFrame,
               column: str) -> pd.DataFrame:
    """Empile les deux années sur une colonne harmonisée, modalités exclues retirées.

    Renvoie un DataFrame à deux colonnes : `year` et `column`.
    """
    if column in NOT_COMPARABLE or column not in COLUMN_MAP.values():
        raise ValueError(f"{column} n'est pas harmonisée entre 2025 et 2026 : "
                         "voir docs/harmonisation_2025_2026.md")
    both = pd.concat([df_2026[["year", column]], df_2025_harmonised[["year", column]]],
                     ignore_index=True)
    excluded = EXCLUDE_VALUES.get(column)
    if excluded:
        both = both[~both[column].isin(excluded)]
    return both
