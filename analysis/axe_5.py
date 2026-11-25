"""Axe 5 — Apprentissage (exemple à remplacer par l'axe choisi).

Responsable : à compléter (voir CADRAGE.md).
Toute la logique propre à cet axe vit ici, sans Streamlit ; la page pages/5_Axe_5.py
ne fait qu'afficher. Travaillez sur la branche axe-5.
"""
from __future__ import annotations

import pandas as pd

from analysis import indicators

QUESTION = "LearnCodeHow"

# Filtre propre à l'axe (en plus des filtres de population communs).
AXIS_FILTER = "Age"


def filter_axis(df: pd.DataFrame, values: list[str]) -> pd.DataFrame:
    """Garde les répondants dont Age est dans `values` ; liste vide = pas de filtre."""
    return df[df[AXIS_FILTER].isin(values)] if values else df


def main_table(df: pd.DataFrame) -> pd.DataFrame:
    """Renvoie la table de la figure principale : part des répondants par modalité de
    LearnCodeHow (choix multiples), avec effectif et base."""
    return indicators.share_multi(df, QUESTION)
