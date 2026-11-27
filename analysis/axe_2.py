"""
Axe 2 — Freins et confiance.
"""
from __future__ import annotations
import pandas as pd
from analysis import indicators

QUESTION = "AIAvoid" 
AXIS_FILTER = "Age"

# Les 8 pays européens les plus représentés (hors France)
PAYS_CIBLES = [
    "Germany", "United Kingdom", "Netherlands", "France", 
    "Poland", "Spain", "Italy", "Sweden", "Switzerland"
]

# Dictionnaire de traduction
TRADUCTION_AIAVOID = {
    "I do not avoid using AI at work or school": "Je n'évite pas l'IA",
    "Issues with privacy or security": "Problèmes de confidentialité/sécurité",
    "Concern over losing job skills or training an AI to replace you": "Peur de perdre ses compétences/remplacement",
    "Moral or ethical concerns": "Préoccupations morales/éthiques",
    "Environmental concerns": "Préoccupations environnementales",
    "Difficulty or lack of training": "Manque de formation",
    "Other, please specify:": "Autre"
}

def filter_axis(df: pd.DataFrame, values: list[str]) -> pd.DataFrame:
    """Garde les répondants dont Age est dans values."""
    return df[df[AXIS_FILTER].isin(values)] if values else df

# ⚠️ C'EST CETTE FONCTION QUI MANQUAIT
def filter_countries(df: pd.DataFrame, values: list[str]) -> pd.DataFrame:
    """Garde les répondants dont le pays est dans values."""
    return df[df['Country'].isin(values)] if values else df

def main_table(df: pd.DataFrame) -> pd.DataFrame:
    """Renvoie la table traduite en français pour la figure principale."""
    df_table = indicators.share_multi(df, QUESTION)
    if 'option' in df_table.columns:
        df_table['option'] = df_table['option'].replace(TRADUCTION_AIAVOID)
    return df_table