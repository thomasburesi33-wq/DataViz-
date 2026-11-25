"""Axe 1 — Organisation du travail (exemple à remplacer par l'axe choisi).

Responsable : à compléter (voir CADRAGE.md).
Toute la logique propre à cet axe vit ici, sans Streamlit ; la page pages/1_Axe_1.py
ne fait qu'afficher. Travaillez sur la branche axe-1.
"""
from __future__ import annotations

import pandas as pd

from analysis import indicators

QUESTION = "WorkSetting"

# Filtre propre à l'axe (en plus des filtres de population communs).
AXIS_FILTER = "OrgSize"


def filter_axis(df: pd.DataFrame, values: list[str]) -> pd.DataFrame:
    """Garde les répondants dont OrgSize est dans `values` ; liste vide = pas de filtre."""
    return df[df[AXIS_FILTER].isin(values)] if values else df


def main_table(df: pd.DataFrame) -> pd.DataFrame:
    """Renvoie la table de la figure principale : part des répondants par modalité de
    WorkSetting (choix unique), avec effectif et base."""
    return indicators.share_single(df, QUESTION)
