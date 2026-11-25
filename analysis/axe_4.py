"""Axe 4 — Rémunération (exemple à remplacer par l'axe choisi).

Responsable : à compléter (voir CADRAGE.md).
Toute la logique propre à cet axe vit ici, sans Streamlit ; la page pages/4_Axe_4.py
ne fait qu'afficher. Travaillez sur la branche axe-4.
"""
from __future__ import annotations

import pandas as pd

from analysis import indicators

QUESTION = "ConvertedCompYearly"
BY = "OrgSize"

# Filtre propre à l'axe (en plus des filtres de population communs).
AXIS_FILTER = "Role"


def filter_axis(df: pd.DataFrame, values: list[str]) -> pd.DataFrame:
    """Garde les répondants dont Role est dans `values` ; liste vide = pas de filtre."""
    return df[df[AXIS_FILTER].isin(values)] if values else df


def main_table(df: pd.DataFrame) -> pd.DataFrame:
    """Renvoie la table de la figure principale : médiane de ConvertedCompYearly par OrgSize,
    avec l'effectif de chaque groupe (médiane masquée sous config.MIN_N répondants)."""
    return indicators.median_by(df, QUESTION, BY)
