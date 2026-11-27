"""Axe 4 — Usages, impact et organisation : pour quelles tâches l'IA est-elle utile,
à quel prix en erreurs, et comment les entreprises comparables l'encadrent-elles ?

Question de la DSI : quelles tâches autoriser, avec quel cadre ?
Toute la logique de l'axe vit ici, sans Streamlit ; pages/4_Axe_4.py ne fait qu'afficher.
La comparaison France / Europe réutilise analysis/accueil.py (mêmes pays, même seuil).
"""
from __future__ import annotations

import pandas as pd

from analysis import accueil

# Les 7 tâches de l'enquête : AIImpact_k (utilité) et AISat_k (satisfaction) portent
# sur la même tâche k (colonne « sub » du schéma 2026).
TACHES = {
    1: "Conception",
    2: "Implémentation",
    3: "Revue de code",
    4: "Débogage / refactoring",
    5: "Documentation",
    6: "Exploration d'architecture",
    7: "Communication",
}
UTILE = {"Useful", "Very useful"}
NON_APPLICABLE = "Not applicable"
AMELIORE = {"Somewhat improved", "Greatly improved"}
DEGRADE = {"Somewhat decreased", "Greatly decreased"}

ERREURS_FR = {
    "Plausible but wrong code": "Code plausible mais faux",
    "Hard-to-review generated code": "Code généré difficile à relire",
    "Missing context": "Contexte manquant",
    "Hallucinated package/config": "Paquet ou configuration inventés",
    "Incorrect or stale internal knowledge": "Connaissances internes fausses ou périmées",
    "Outdated APIs": "API obsolètes",
    "Security/privacy issue": "Problème de sécurité ou de confidentialité",
    "Poor debugging path": "Mauvaise piste de débogage",
    "Licensing/source uncertainty": "Licence ou source incertaine",
    "Other, please specify": "Autre",
}

POLITIQUES_FR = {
    "AI use is mostly optional and left up to individuals": "Usage libre, laissé à chacun",
    "My organization provides approved AI tools and guidance for how to use them":
        "Outils approuvés et consignes",
    "Some teams actively encourage AI use, but practices vary across the organization":
        "Encouragé par certaines équipes",
    "My organization expects some employees to use AI tools for certain types of work":
        "Usage attendu pour certaines tâches",
    "My organization measures or evaluates AI use as part of employee or team performance":
        "Usage mesuré dans l'évaluation",
    "My organization does not currently use AI tools or agents for work": "Pas d'IA",
    "Not sure": "Ne sait pas",
}

GRANDES = {"1,000 to 4,999 employees", "5,000 to 9,999 employees", "10,000 or more employees"}
PETITES = {"Less than 20 employees", "20 to 99 employees", "100 to 499 employees",
           "500 to 999 employees"}


def _part_reponses(serie: pd.Series, reponses: set[str],
                   exclure: set[str] = frozenset()) -> tuple[float | None, int, int]:
    """(part, n, base) des réponses appartenant à `reponses`, parmi les réponses non vides
    qui ne sont pas dans `exclure`."""
    repondu = serie.dropna()
    repondu = repondu[~repondu.isin(exclure)]
    base = len(repondu)
    n = int(repondu.isin(reponses).sum())
    return (n / base if base else None), n, base


def utilite_par_tache(sel: pd.DataFrame, exclure_na: bool = False) -> pd.DataFrame:
    """Part des répondants jugeant l'IA utile ou très utile, par tâche et par zone.

    Colonnes : tache, Zone, part, n, base. `exclure_na=True` retire « Not applicable »
    de la base (choix documenté dans DECISIONS.md).
    """
    exclure = {NON_APPLICABLE} if exclure_na else set()
    lignes = []
    for k, tache in TACHES.items():
        for zone in ("France", "Europe"):
            p, n, base = _part_reponses(sel.loc[sel["Zone"] == zone, f"AIImpact_{k}"],
                                        UTILE, exclure)
            lignes.append({"tache": tache, "Zone": zone, "part": p, "n": n, "base": base})
    return pd.DataFrame(lignes)


def satisfaction_par_tache(sel: pd.DataFrame, zone: str = "France") -> pd.DataFrame:
    """Part de satisfaction améliorée et dégradée par l'IA, par tâche, pour une zone.

    Colonnes : tache, ameliore, degrade, base.
    """
    lignes = []
    for k, tache in TACHES.items():
        serie = sel.loc[sel["Zone"] == zone, f"AISat_{k}"]
        p_plus, _, base = _part_reponses(serie, AMELIORE)
        p_moins, _, _ = _part_reponses(serie, DEGRADE)
        lignes.append({"tache": tache, "ameliore": p_plus, "degrade": p_moins, "base": base})
    return pd.DataFrame(lignes)


def erreurs_couteuses(sel: pd.DataFrame) -> pd.DataFrame:
    """Erreurs de l'IA qui ont coûté le plus de temps (Disruption, choix multiples),
    par zone. Colonnes : erreur, Zone, part, n, base."""
    lignes = []
    for zone in ("France", "Europe"):
        serie = sel.loc[sel["Zone"] == zone, "Disruption"].dropna()
        base = len(serie)
        choix = serie.str.split(";").explode()
        for code, libelle in ERREURS_FR.items():
            n = int((choix == code).sum())
            lignes.append({"erreur": libelle, "Zone": zone, "n": n, "base": base,
                           "part": n / base if base else None})
    return pd.DataFrame(lignes)


def politique_par_taille(sel: pd.DataFrame, zone: str = "France") -> pd.DataFrame:
    """Politique d'usage de l'IA (AIUse) selon la taille d'entreprise, pour une zone.

    Deux groupes : « 1 000 salariés et plus » et « Moins de 1 000 salariés » (les
    indépendants et « je ne sais pas » sont écartés). Colonnes : taille, politique, part,
    n, base.
    """
    d = sel[(sel["Zone"] == zone) & sel["AIUse"].notna()]
    groupes = {"1 000 salariés et plus": GRANDES, "Moins de 1 000 salariés": PETITES}
    lignes = []
    for taille, valeurs in groupes.items():
        g = d[d["OrgSize"].isin(valeurs)]
        base = len(g)
        for code, libelle in POLITIQUES_FR.items():
            n = int((g["AIUse"] == code).sum())
            lignes.append({"taille": taille, "politique": libelle, "n": n, "base": base,
                           "part": n / base if base else None})
    return pd.DataFrame(lignes)


def indicateurs(sel: pd.DataFrame, exclure_na: bool = False) -> list[dict]:
    """Les 4 chiffres du bandeau, pour la France, avec la valeur Europe et la base."""
    util = utilite_par_tache(sel, exclure_na).set_index(["tache", "Zone"])
    sat_fr = satisfaction_par_tache(sel, "France").set_index("tache")
    sat_eu = satisfaction_par_tache(sel, "Europe").set_index("tache")
    err = erreurs_couteuses(sel).set_index(["erreur", "Zone"])
    pol_fr = politique_par_taille(sel, "France").set_index(["taille", "politique"])
    pol_eu = politique_par_taille(sel, "Europe").set_index(["taille", "politique"])
    grand, outils = "1 000 salariés et plus", "Outils approuvés et consignes"
    return [
        {"libelle": "Jugent l'IA utile pour l'implémentation",
         "france": util.loc[("Implémentation", "France"), "part"],
         "europe": util.loc[("Implémentation", "Europe"), "part"],
         "base": util.loc[("Implémentation", "France"), "base"]},
        {"libelle": "Satisfaction en baisse sur l'implémentation",
         "france": sat_fr.loc["Implémentation", "degrade"],
         "europe": sat_eu.loc["Implémentation", "degrade"],
         "base": sat_fr.loc["Implémentation", "base"]},
        {"libelle": "Ont perdu du temps à cause de code plausible mais faux",
         "france": err.loc[("Code plausible mais faux", "France"), "part"],
         "europe": err.loc[("Code plausible mais faux", "Europe"), "part"],
         "base": err.loc[("Code plausible mais faux", "France"), "base"]},
        {"libelle": "Grandes entreprises : outils approuvés et consignes",
         "france": pol_fr.loc[(grand, outils), "part"],
         "europe": pol_eu.loc[(grand, outils), "part"],
         "base": pol_fr.loc[(grand, outils), "base"]},
    ]
