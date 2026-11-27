"""Axe 1 · Adoption : où en sont les développeurs ?

Question de la DSI : qui utilise l'IA au travail, quels types d'outils, à quelle fréquence,
et qui se forme ? La France est comparée aux pays européens de la page principale.

Responsable : Baptiste Lemaître (branche axe-1).
Fonctions pures, sans Streamlit : la page pages/1_Axe_1.py ne fait qu'afficher les tables
renvoyées ici. Les libellés des réponses sont ceux de l'enquête 2026, à l'identique.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

from analysis import accueil

FRANCE = accueil.FRANCE
MIN_REPONDANTS = accueil.MIN_REPONDANTS  # même seuil que la page principale (DECISIONS.md)
Z_95 = 1.96  # quantile de la loi normale pour un intervalle de confiance à 95 %

# --- Les questions de l'axe ------------------------------------------------------------
# AISelect : « Utilisez-vous des outils ou agents d'IA dans votre rôle au travail ? »
# (choix multiples). AIFreq_k : fréquence d'usage de l'outil k, posée seulement à ceux qui
# l'ont coché dans AISelect, dans le même ordre (vérifié sur les données).
NON_UTILISATEUR = "I don’t use AI tools"
OUTILS = [
    # (réponse AISelect, libellé affiché, colonne de fréquence)
    ("AI coding assistants or coding agents", "Assistants ou agents de code", "AIFreq_1"),
    ("General-purpose AI chat tools", "Chatbots généralistes", "AIFreq_2"),
    ("AI agents or automated workflows", "Agents IA et workflows automatisés", "AIFreq_3"),
    ("Internal AI tools built by my company", "Outils IA internes à l'entreprise", "AIFreq_4"),
]
FREQUENCES_FR = {"Daily": "Chaque jour", "Weekly": "Chaque semaine",
                 "Monthly or Infrequent": "Chaque mois ou moins"}

# AIDaily : temps passé avec l'IA, posé seulement à ceux qui utilisent un outil chaque jour.
TEMPS_QUOTIDIEN_FR = {
    "<1 hour and not every day": "Moins d'1 h, pas tous les jours",
    "<1 hour every day": "Moins d'1 h par jour",
    "1-2 hours/day": "1 à 2 h par jour",
    "2-4 hours/day": "2 à 4 h par jour",
    "4+ hours/day": "4 h et plus par jour",
}

# LearnAI : s'est-on formé à l'IA l'an dernier ? LearnAIHow (choix multiples) : comment,
# posé seulement à ceux qui ont répondu oui.
FORMATION_FR = {
    "No": "Non",
    "Yes, on my own": "Oui, par soi-même",
    "Yes, at work": "Oui, au travail",
    "Yes, both on my own and at work": "Oui, par soi-même et au travail",
}
MOYENS_FORMATION = [
    ("Colleague or on-the-job training", "Collègues ou formation sur le poste"),
    ("Technical documentation (is generated for/by the tool or system)",
     "Documentation technique"),
    ("AI CodeGen tools or AI-enabled apps", "Les outils d'IA eux-mêmes"),
    ("Other online resources (e.g. standard search, forum, online community)",
     "Ressources en ligne (recherche, forums)"),
    ("Videos (not associated with specific online course or certification)", "Vidéos"),
    ("Blogs or podcasts", "Blogs ou podcasts"),
    ("Online Courses or Certification (includes all media types)",
     "Cours en ligne ou certification"),
    ("School (i.e., University, College, etc)", "École ou université"),
]

# --- Les segments ----------------------------------------------------------------------
AGES_FR = {
    "Under 18 years old": "Moins de 18 ans", "18-24 years old": "18-24 ans",
    "25-34 years old": "25-34 ans", "35-44 years old": "35-44 ans",
    "45-54 years old": "45-54 ans", "55-64 years old": "55-64 ans",
    "65 years or older": "65 ans et plus", "Prefer not to say": "Non précisé",
}
EXPERIENCES = ["0 à 4 ans", "5 à 9 ans", "10 à 19 ans", "20 ans et plus"]
POSTES = ["Développeurs", "Architectes et managers", "Data, IA et infrastructure",
          "Étudiants", "Autres postes"]
_ARCHITECTES_MANAGERS = {
    "Architect, software or solutions", "Engineering manager",
    "Senior executive (C-suite, VP, etc.)", "Project manager", "Product manager",
    "Founder or entrepreneur",
}
_DATA_INFRA = {
    "Data engineer", "Data scientist", "AI/ML engineer", "Applied scientist",
    "Data or business analyst", "DevOps engineer or professional",
    "Cloud infrastructure engineer", "System administrator", "Site reliability engineer",
    "Platform engineer", "Database administrator or engineer",
    "Cybersecurity or InfoSec professional",
}
SITUATIONS_FR = {
    "Employed": "Salariés",
    "Independent contractor, freelancer, or self-employed": "Indépendants",
    "Student": "Étudiants",
    "Not employed": "Sans emploi",
    "Retired": "Retraités",
    "I prefer not to say": "Non précisé",
}
SEGMENTS = {  # libellé affiché -> colonne ajoutée par preparer()
    "Âge": "Age",
    "Expérience professionnelle": "Experience",
    "Poste": "Poste",
    "Situation professionnelle": "Situation",
}


def tranche_experience(annees: float) -> str | None:
    """Tranche d'expérience professionnelle (WorkExp, en années) ; None si non renseignée."""
    if pd.isna(annees):
        return None
    if annees < 5:
        return EXPERIENCES[0]
    if annees < 10:
        return EXPERIENCES[1]
    if annees < 20:
        return EXPERIENCES[2]
    return EXPERIENCES[3]


def groupe_poste(role: str) -> str | None:
    """Regroupe les 41 postes de l'enquête (Role) en 5 familles assez nombreuses."""
    if pd.isna(role):
        return None
    if role.startswith("Developer") or role == "Software engineer":
        return "Développeurs"
    if role in _ARCHITECTES_MANAGERS:
        return "Architectes et managers"
    if role in _DATA_INFRA:
        return "Data, IA et infrastructure"
    if role == "Student":
        return "Étudiants"
    return "Autres postes"


def _contient(serie: pd.Series, reponse: str) -> pd.Series:
    """1.0 si la réponse à choix multiples (« a;b;c ») contient `reponse`, 0.0 sinon,
    NaN si la personne n'a pas répondu à la question."""
    return serie.str.split(";").apply(
        lambda choix: float(reponse in choix) if isinstance(choix, list) else np.nan
    ).astype("float")


def _indicatrice(condition: pd.Series, repondu: pd.Series) -> pd.Series:
    """1.0 / 0.0 pour ceux qui ont répondu, NaN pour les autres (hors base)."""
    return condition.astype("float").where(repondu)


# --- Le catalogue des indicateurs -----------------------------------------------------
# Chaque indicateur est une colonne 0/1 ajoutée par preparer(), NaN hors de sa base :
# la part est la moyenne sur les seuls répondants concernés. (thème, libellé, base)
INDICATEURS: dict[str, tuple[str, str, str]] = {
    "utilise_ia": ("Adoption", "Utilisent l'IA au travail",
                   "répondants à la question sur l'usage de l'IA au travail"),
    **{f"outil_{k}": ("Adoption", libelle,
                      "répondants à la question sur l'usage de l'IA au travail")
       for k, (_, libelle, _) in enumerate(OUTILS, 1)},
    "quotidien": ("Fréquence", "Utilisent au moins un outil chaque jour",
                  "utilisateurs d'IA au travail"),
    **{f"quotidien_{k}": ("Fréquence", f"{libelle} : chaque jour",
                          f"utilisateurs de ce type d'outil ({libelle.lower()})")
       for k, (_, libelle, _) in enumerate(OUTILS, 1)},
    "plus_2h": ("Fréquence", "Plus de 2 h d'IA par jour",
                "utilisateurs quotidiens ayant répondu sur le temps passé"),
    "forme": ("Formation", "Se sont formés à l'IA l'an dernier",
              "répondants à la question sur la formation à l'IA"),
    "forme_travail": ("Formation", "Se sont formés à l'IA au travail",
                      "répondants à la question sur la formation à l'IA"),
    **{f"moyen_{k}": ("Formation", f"Formés via : {libelle[0].lower() + libelle[1:]}",
                      "répondants formés à l'IA ayant dit comment")
       for k, (_, libelle) in enumerate(MOYENS_FORMATION, 1)},
}


def libelle(indicateur: str) -> str:
    """Libellé affiché d'un indicateur du catalogue."""
    return INDICATEURS[indicateur][1]


def preparer(df: pd.DataFrame) -> pd.DataFrame:
    """Ajoute à l'enquête les colonnes de segments (Experience, Poste, Situation) et une
    colonne 0/1 par indicateur du catalogue (NaN pour les personnes hors de sa base)."""
    selection = df["AISelect"]
    non_utilisateur = _contient(selection, NON_UTILISATEUR)
    utilise = 1.0 - non_utilisateur  # NaN reste NaN : hors base
    cols = {
        "Experience": df["WorkExp"].map(tranche_experience),
        "Poste": df["Role"].map(groupe_poste),
        "Situation": df["Employment"].map(SITUATIONS_FR),
        "utilise_ia": utilise,
    }
    quotidiens = []
    for k, (reponse, _, freq) in enumerate(OUTILS, 1):
        cols[f"outil_{k}"] = _contient(selection, reponse)
        cols[f"quotidien_{k}"] = _indicatrice(df[freq].eq("Daily"), df[freq].notna())
        quotidiens.append(df[freq].eq("Daily"))
    cols["quotidien"] = _indicatrice(pd.concat(quotidiens, axis=1).any(axis=1), utilise.eq(1))
    cols["plus_2h"] = _indicatrice(df["AIDaily"].isin(["2-4 hours/day", "4+ hours/day"]),
                                   df["AIDaily"].notna())
    formation = df["LearnAI"]
    cols["forme"] = _indicatrice(formation.ne("No"), formation.notna())
    cols["forme_travail"] = _indicatrice(
        formation.isin(["Yes, at work", "Yes, both on my own and at work"]), formation.notna())
    for k, (reponse, _) in enumerate(MOYENS_FORMATION, 1):
        cols[f"moyen_{k}"] = _contient(df["LearnAIHow"], reponse)
    return df.assign(**cols)


def filtrer(df: pd.DataFrame, europe: list[str], ages: list[str] | None = None,
            experiences: list[str] | None = None, postes: list[str] | None = None,
            situations: list[str] | None = None) -> pd.DataFrame:
    """France + pays européens choisis, avec la colonne Zone (« France » ou « Europe »).
    Chaque liste vide ou None signifie « pas de filtre sur ce segment »."""
    sel = accueil.filtrer(df, europe, ages)
    for colonne, valeurs in (("Experience", experiences), ("Poste", postes),
                             ("Situation", situations)):
        if valeurs:
            sel = sel[sel[colonne].isin(valeurs)]
    return sel


# --- Format des nombres à la française --------------------------------------------------

def fr_pct(valeur: float | None, decimales: int = 0) -> str:
    """Part en pourcentage, à la française : 0.753 -> « 75 % » ; None -> « — »."""
    if valeur is None or pd.isna(valeur):
        return "—"
    return f"{100 * valeur:.{decimales}f}".replace(".", ",") + "\u00a0%"


def fr_pts(points: float, decimales: int = 1) -> str:
    """Écart signé en points, à la française : -6.84 -> « −6,8 pts »."""
    if pd.isna(points):
        return "—"
    texte = f"{points:+.{decimales}f}".replace(".", ",").replace("-", "\u2212")
    return texte + "\u00a0pts"


def fr_n(n: int) -> str:
    """Effectif avec séparateur de milliers : 5072 -> « 5 072 »."""
    return f"{n:,}".replace(",", "\u202f")


# --- Les calculs ----------------------------------------------------------------------

def marge(part_: float | None, base: int) -> float:
    """Demi-largeur de l'intervalle de confiance à 95 % d'une part (loi normale)."""
    if part_ is None or not base:
        return float("nan")
    return Z_95 * math.sqrt(part_ * (1 - part_) / base)


def part(df: pd.DataFrame, indicateur: str) -> tuple[float | None, int, int]:
    """(part, nombre concerné, base) d'un indicateur parmi les personnes de sa base."""
    valeurs = df[indicateur].dropna()
    base = len(valeurs)
    if not base:
        return None, 0, 0
    return float(valeurs.mean()), int(valeurs.sum()), base


def tableau(sel: pd.DataFrame, indicateurs: list[str]) -> pd.DataFrame:
    """Une ligne par indicateur et par zone : code, indicateur, Zone, part, n, base, marge,
    base_texte. C'est la table derrière les figures en haltères."""
    lignes = []
    for ind in indicateurs:
        for zone in ("France", "Europe"):
            p, n, base = part(sel[sel["Zone"] == zone], ind)
            lignes.append({"code": ind, "indicateur": libelle(ind), "Zone": zone, "part": p,
                           "n": n, "base": base, "marge": marge(p, base),
                           "base_texte": INDICATEURS[ind][2]})
    return pd.DataFrame(lignes)


def ecart(sel: pd.DataFrame, indicateur: str) -> dict:
    """Écart France - Europe en points, avec son intervalle de confiance à 95 %.

    Renvoie france, europe, base_france, base_europe, ecart et marge (en points) ;
    `significatif` est vrai quand l'intervalle ne contient pas zéro.
    """
    pf, _, nf = part(sel[sel["Zone"] == "France"], indicateur)
    pe, _, ne = part(sel[sel["Zone"] == "Europe"], indicateur)
    if pf is None or pe is None:
        return {"france": pf, "europe": pe, "base_france": nf, "base_europe": ne,
                "ecart": float("nan"), "marge": float("nan"), "significatif": False}
    diff = 100 * (pf - pe)
    m = 100 * Z_95 * math.sqrt(pf * (1 - pf) / nf + pe * (1 - pe) / ne)
    return {"france": pf, "europe": pe, "base_france": nf, "base_europe": ne,
            "ecart": diff, "marge": m, "significatif": abs(diff) > m}


def par_pays(sel: pd.DataFrame, indicateur: str) -> pd.DataFrame:
    """Une ligne par pays (nom français) : pays, part, n, base, france (booléen),
    triée par part décroissante."""
    lignes = []
    for pays, groupe in sel.groupby("Country"):
        p, n, base = part(groupe, indicateur)
        lignes.append({"pays": accueil.NOMS_FR.get(pays, pays), "part": p, "n": n,
                       "base": base, "france": pays == FRANCE})
    if not lignes:
        return pd.DataFrame(columns=["pays", "part", "n", "base", "france"])
    return pd.DataFrame(lignes).sort_values("part", ascending=False, ignore_index=True)


def ordre_segment(segment: str, valeurs: list[str]) -> list[str]:
    """Ordre d'affichage naturel des modalités d'un segment (âges, expériences…)."""
    if segment == "Age":
        return [a for a in AGES_FR if a in valeurs]
    reference = {"Experience": EXPERIENCES, "Poste": POSTES,
                 "Situation": list(SITUATIONS_FR.values())}.get(segment, sorted(valeurs))
    return [v for v in reference if v in valeurs]


def par_segment(sel: pd.DataFrame, indicateur: str, segment: str) -> pd.DataFrame:
    """Une ligne par modalité du segment et par zone : segment, Zone, part, n, base,
    affiche (base au moins égale au seuil). Les répondants sans modalité sont exclus."""
    lignes = []
    for valeur in ordre_segment(segment, sel[segment].dropna().unique().tolist()):
        groupe = sel[sel[segment] == valeur]
        for zone in ("France", "Europe"):
            p, n, base = part(groupe[groupe["Zone"] == zone], indicateur)
            lignes.append({"segment": AGES_FR.get(valeur, valeur), "Zone": zone, "part": p,
                           "n": n, "base": base, "affiche": base >= MIN_REPONDANTS})
    return pd.DataFrame(lignes, columns=["segment", "Zone", "part", "n", "base", "affiche"])


def ecarts_par_segment(sel: pd.DataFrame, indicateur: str, segment: str) -> pd.DataFrame:
    """Écart France - Europe (en points) dans chaque modalité du segment où les deux zones
    atteignent le seuil d'effectif : segment, france, europe, ecart, marge, base_france,
    base_europe."""
    lignes = []
    for valeur in ordre_segment(segment, sel[segment].dropna().unique().tolist()):
        e = ecart(sel[sel[segment] == valeur], indicateur)
        if e["base_france"] >= MIN_REPONDANTS and e["base_europe"] >= MIN_REPONDANTS:
            lignes.append({"segment": AGES_FR.get(valeur, valeur), "france": e["france"],
                           "europe": e["europe"], "ecart": e["ecart"], "marge": e["marge"],
                           "base_france": e["base_france"], "base_europe": e["base_europe"]})
    return pd.DataFrame(lignes, columns=["segment", "france", "europe", "ecart", "marge",
                                         "base_france", "base_europe"])


def europe_a_composition_francaise(sel: pd.DataFrame, indicateur: str,
                                   segment: str) -> float | None:
    """Part européenne recalculée comme si l'Europe avait la même répartition que la
    France sur `segment` (standardisation directe). Si elle reste loin de la part
    française, la composition des répondants n'explique pas l'écart."""
    base = sel[sel[indicateur].notna() & sel[segment].notna()]
    poids = base.loc[base["Zone"] == "France", segment].value_counts(normalize=True)
    taux = base[base["Zone"] == "Europe"].groupby(segment)[indicateur].mean()
    communs = poids.index.intersection(taux.index)
    if communs.empty:
        return None
    return float((taux[communs] * poids[communs]).sum() / poids[communs].sum())


def repartition(sel: pd.DataFrame, colonne: str, libelles: dict[str, str]) -> pd.DataFrame:
    """Répartition d'une question à choix unique par zone : Zone, reponse (libellé
    français), ordre (rang dans `libelles`), part, n, base."""
    lignes = []
    for zone in ("France", "Europe"):
        reponses = sel.loc[sel["Zone"] == zone, colonne].dropna()
        base = len(reponses)
        comptes = reponses.value_counts()
        for rang, (brut, fr) in enumerate(libelles.items()):
            n = int(comptes.get(brut, 0))
            lignes.append({"Zone": zone, "reponse": fr, "ordre": rang,
                           "part": n / base if base else None, "n": n, "base": base})
    return pd.DataFrame(lignes)


def entonnoir(sel: pd.DataFrame) -> pd.DataFrame:
    """Qui répond à quoi : effectifs par étape du questionnaire, pour chaque zone.
    Les questions de l'axe ne sont pas posées à tout le monde (filtrage de l'enquête)."""
    etapes = [
        ("Répondants retenus (pays et filtres)", lambda d: len(d)),
        ("Ont répondu sur l'usage de l'IA au travail",
         lambda d: int(d["utilise_ia"].notna().sum())),
        ("… dont utilisent l'IA au travail", lambda d: int(d["utilise_ia"].eq(1).sum())),
        ("… dont l'utilisent chaque jour", lambda d: int(d["quotidien"].eq(1).sum())),
        ("Ont répondu sur la formation à l'IA", lambda d: int(d["forme"].notna().sum())),
        ("… dont se sont formés à l'IA", lambda d: int(d["forme"].eq(1).sum())),
    ]
    return pd.DataFrame([{"etape": nom, **{zone: f(sel[sel["Zone"] == zone])
                                            for zone in ("France", "Europe")}}
                         for nom, f in etapes])


# --- La table de preuves --------------------------------------------------------------

def table_de_preuves(sel: pd.DataFrame) -> pd.DataFrame:
    """Met à l'épreuve l'affirmation centrale de l'axe : « en France, moins de répondants
    utilisent l'IA au travail qu'en Europe ». Chaque test pourrait échouer.

    Une ligne par test : test, resultat (texte chiffré), tient (True, False, ou None si le
    test n'est pas calculable faute d'effectif).
    """
    tests = []
    e = ecart(sel, "utilise_ia")
    if e["france"] is None or e["europe"] is None:
        return pd.DataFrame([{"test": "Comparaison France / Europe",
                              "resultat": "Effectif insuffisant", "tient": None}])
    tests.append({
        "test": "Comparaison juste : l'écart dépasse-t-il la marge d'erreur ?",
        "resultat": (f"France {fr_pct(e['france'], 1)} (n = {fr_n(e['base_france'])}), "
                     f"Europe {fr_pct(e['europe'], 1)} (n = {fr_n(e['base_europe'])}) : "
                     f"écart de {fr_pts(e['ecart'])}, à ± {fr_pts(e['marge']).lstrip('+')} "
                     "près (intervalle de confiance à 95 %)"),
        "tient": bool(e["significatif"] and e["ecart"] < 0),
    })

    pays = par_pays(sel, "utilise_ia")
    pays = pays[pays["base"] >= MIN_REPONDANTS]
    autres = pays[~pays["france"]]
    fr = pays.loc[pays["france"], "part"]
    if not fr.empty and not autres.empty:
        au_dessus = autres[autres["part"] > fr.iloc[0]]
        tests.append({
            "test": "Pays par pays : la France est-elle sous chacun de ses voisins ?",
            "resultat": (f"La France est sous {len(au_dessus)} des {len(autres)} pays "
                         f"comparables (au moins {MIN_REPONDANTS} répondants)"),
            "tient": len(au_dessus) == len(autres),
        })

    for nom, segment in (("l'expérience professionnelle", "Experience"), ("l'âge", "Age"),
                         ("le poste", "Poste"), ("la situation professionnelle", "Situation")):
        seg = ecarts_par_segment(sel, "utilise_ia", segment)
        if seg.empty:
            tests.append({"test": f"Segmenter selon {nom}",
                          "resultat": "Aucun segment n'atteint le seuil d'effectif",
                          "tient": None})
            continue
        negatifs = int((seg["ecart"] < 0).sum())
        tests.append({
            "test": f"Segmenter selon {nom} : l'écart tient-il dans chaque groupe ?",
            "resultat": (f"France en dessous dans {negatifs} groupe(s) sur {len(seg)} : "
                         + " · ".join(f"{r.segment} {fr_pts(r.ecart, 0)}"
                                      for r in seg.itertuples())),
            "tient": negatifs == len(seg),
        })

    for nom, segment in (("d'âge", "Age"), ("d'expérience", "Experience"),
                         ("de postes", "Poste")):
        standard = europe_a_composition_francaise(sel, "utilise_ia", segment)
        if standard is None:
            continue
        reste = 100 * (e["france"] - standard)
        tests.append({
            "test": f"Autre explication : une répartition {nom} différente en France ?",
            "resultat": (f"Avec la même répartition {nom} que la France, l'Europe serait à "
                         f"{fr_pct(standard, 1)} (au lieu de {fr_pct(e['europe'], 1)}) : "
                         f"l'écart reste de {fr_pts(reste)}"),
            "tient": reste < 0 and abs(reste) > e["marge"],
        })
    return pd.DataFrame(tests, columns=["test", "resultat", "tient"])
