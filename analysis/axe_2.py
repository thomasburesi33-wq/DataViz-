"""
Axe 2 — Freins et confiance.

Responsable : [Votre Prénom/Nom] (voir CADRAGE.md).
Toute la logique propre à cet axe vit ici, sans Streamlit ; la page pages/2_Axe_2.py
ne fait qu'afficher. Travaillez sur la branche axe-2.
"""
from __future__ import annotations

import pandas as pd

from analysis import indicators

# Variables de votre axe
QUESTION = "AIAvoid"  # La question principale qu'on étudie
AXIS_FILTER = "Age"    # Le filtre propre à l'axe

def filter_axis(df: pd.DataFrame, values: list[str]) -> pd.DataFrame:
    """Garde les répondants dont Age est dans `values` ; liste vide = pas de filtre."""
    return df[df[AXIS_FILTER].isin(values)] if values else df


def main_table(df: pd.DataFrame) -> pd.DataFrame:
    """Renvoie la table de la figure principale : part des répondants par modalité de AIAvoid, avec effectif et base."""
    # On utilise l'indicateur de part pour les choix multiples ou uniques
    return indicators.share_multi(df, QUESTION)