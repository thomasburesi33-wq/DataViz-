"""Figure de la page principale : la France face à ses voisins européens sur l'IA.

Question à laquelle répond la figure : les répondants vivant en France se distinguent-ils
de leurs voisins européens dans leur rapport à l'IA, et sur quoi (usage, freins, confiance) ?

Fonctions pures, sans Streamlit : app.py ne fait qu'afficher la table renvoyée ici.
"""
from __future__ import annotations

import pandas as pd

FRANCE = "France"

# Pays européens comparés par défaut (choix du groupe, à justifier dans DECISIONS.md).
EUROPE_DEFAUT = [
    "Germany",
    "United Kingdom of Great Britain and Northern Ireland",
    "Netherlands",
    "Spain",
    "Italy",
    "Poland",
    "Sweden",
    "Switzerland",
]

# Noms des pays en français pour l'affichage.
NOMS_FR = {
    "France": "France", "Germany": "Allemagne",
    "United Kingdom of Great Britain and Northern Ireland": "Royaume-Uni",
    "Netherlands": "Pays-Bas", "Spain": "Espagne", "Italy": "Italie", "Poland": "Pologne",
    "Sweden": "Suède", "Switzerland": "Suisse", "Belgium": "Belgique", "Austria": "Autriche",
    "Portugal": "Portugal", "Ireland": "Irlande", "Denmark": "Danemark", "Norway": "Norvège",
    "Finland": "Finlande", "Czech Republic": "Tchéquie", "Greece": "Grèce",
}

# Les 4 indicateurs : (libellé affiché, colonne, réponse comptée, à qui la question est posée).
# Les libellés des réponses sont ceux de l'enquête 2026, à l'identique.
INDICATEURS = [
    ("N'utilisent pas l'IA au travail", "AISelect", "I don’t use AI tools",
     "répondants à la question sur l'usage de l'IA"),
    ("Citent l'environnement comme frein", "AIAvoid", "Environmental concerns",
     "répondants à la question sur les freins"),
    ("N'ont aucune réserve envers l'IA", "AIAvoid", "I do not avoid using AI at work or school",
     "répondants à la question sur les freins"),
    ("Font confiance si le résultat est vérifiable", "AITrust",
     "I trust it when I can easily verify the output",
     "utilisateurs d'IA ayant répondu sur la confiance"),
]


def filtrer(df: pd.DataFrame, europe: list[str], ages: list[str] | None = None) -> pd.DataFrame:
    """Garde la France et les pays de comparaison, ajoute la colonne Zone
    (« France » ou « Europe »). `ages` vide ou None = toutes les tranches d'âge."""
    sel = df[df["Country"].isin([FRANCE] + list(europe))]
    if ages:
        sel = sel[sel["Age"].isin(ages)]
    zone = sel["Country"].eq(FRANCE).map({True: "France", False: "Europe"})
    return sel.assign(Zone=zone)


def part(df: pd.DataFrame, colonne: str, reponse: str) -> tuple[float | None, int, int]:
    """(part, nombre ayant coché `reponse`, base) parmi ceux qui ont répondu à `colonne`.
    Les questions à choix multiples (« a;b;c ») sont gérées."""
    repondu = df[colonne].dropna()
    base = len(repondu)
    n = int(repondu.str.split(";").apply(lambda choix: reponse in choix).sum()) if base else 0
    return (n / base if base else None), n, base


def tableau_france_europe(sel: pd.DataFrame) -> pd.DataFrame:
    """Une ligne par indicateur et par zone : indicateur, Zone, part, n, base, base_texte.

    C'est la table derrière la figure en haltères ; `sel` vient de `filtrer`.
    """
    lignes = []
    for libelle, colonne, reponse, base_texte in INDICATEURS:
        for zone in ("France", "Europe"):
            p, n, base = part(sel[sel["Zone"] == zone], colonne, reponse)
            lignes.append({"indicateur": libelle, "Zone": zone, "part": p, "n": n,
                           "base": base, "base_texte": base_texte})
    return pd.DataFrame(lignes)


def ecarts(tableau: pd.DataFrame) -> pd.DataFrame:
    """Une ligne par indicateur : part France, part Europe et écart en points."""
    large = tableau.pivot(index="indicateur", columns="Zone", values="part")
    large["ecart_points"] = 100 * (large["France"] - large["Europe"])
    ordre = [i[0] for i in INDICATEURS]
    return large.reindex(ordre).reset_index()
