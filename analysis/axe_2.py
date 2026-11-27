"""
Axe 2 — Freins et confiance.
"""
from __future__ import annotations
import pandas as pd
from analysis import indicators

# Variables de votre axe
QUESTION = "AIAvoid" 
AXIS_FILTER = "Age"

def filter_axis(df: pd.DataFrame, values: list[str]) -> pd.DataFrame:
    """Garde les répondants dont Age est dans values."""
    return df[df[AXIS_FILTER].isin(values)] if values else df

def main_table(df: pd.DataFrame) -> pd.DataFrame:
    """Renvoie la table pour la figure principale."""
    return indicators.share_multi(df, QUESTION)