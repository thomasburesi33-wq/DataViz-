"""Tests de l'axe 1 (analysis/axe_1.py), sur des données inventées : aucun téléchargement."""
import math

import pandas as pd
import pytest

from analysis import axe_1 as axe

CODE, CHAT = axe.OUTILS[0][0], axe.OUTILS[1][0]


@pytest.fixture
def brut() -> pd.DataFrame:
    """Six répondants : 4 en France, 2 en Allemagne, un Japonais hors périmètre."""
    return pd.DataFrame({
        "Country": ["France"] * 4 + ["Germany"] * 2 + ["Japan"],
        "Age": ["25-34 years old", "25-34 years old", "35-44 years old", "18-24 years old",
                "25-34 years old", "35-44 years old", "25-34 years old"],
        "WorkExp": [3, 12, None, 25, 7, 4, 2],
        "Role": ["Developer, back-end", "Engineering manager", "Student", "Data engineer",
                 "Developer, full-stack", "Developer, mobile", "Other"],
        "Employment": ["Employed", "Employed", "Student", "Employed", "Employed",
                       "Independent contractor, freelancer, or self-employed", "Employed"],
        "AISelect": [f"{CODE};{CHAT}", axe.NON_UTILISATEUR, None, CHAT, CODE, CODE, CODE],
        "AIFreq_1": ["Daily", None, None, None, "Weekly", "Daily", "Daily"],
        "AIFreq_2": ["Weekly", None, None, "Daily", None, None, None],
        "AIFreq_3": [None] * 7,
        "AIFreq_4": [None] * 7,
        "AIDaily": ["4+ hours/day", None, None, "<1 hour every day", None, "2-4 hours/day",
                    None],
        "LearnAI": ["Yes, at work", "No", "Yes, on my own", None, "Yes, both on my own and at work",
                    "No", "No"],
        "LearnAIHow": ["Colleague or on-the-job training", None, "Blogs or podcasts", None,
                       "Colleague or on-the-job training;Blogs or podcasts", None, None],
    })


@pytest.fixture
def df(brut) -> pd.DataFrame:
    return axe.preparer(brut)


def test_segments(df):
    assert list(df["Experience"][:2]) == ["0 à 4 ans", "10 à 19 ans"]
    assert pd.isna(df["Experience"][2])
    assert list(df["Poste"][:4]) == ["Développeurs", "Architectes et managers", "Étudiants",
                                     "Data, IA et infrastructure"]
    assert df["Situation"][5] == "Indépendants"


def test_indicateurs_respectent_leur_base(df):
    # Pas de réponse à AISelect : hors base (NaN), pas compté comme non-utilisateur.
    assert pd.isna(df.loc[2, "utilise_ia"])
    assert list(df["utilise_ia"][:2]) == [1.0, 0.0]
    assert df.loc[0, "outil_1"] == 1.0 and df.loc[3, "outil_1"] == 0.0
    # La fréquence d'un outil n'est posée qu'à ses utilisateurs.
    assert pd.isna(df.loc[3, "quotidien_1"]) and df.loc[4, "quotidien_1"] == 0.0
    # « Au moins un outil chaque jour » : base = utilisateurs d'IA.
    assert pd.isna(df.loc[1, "quotidien"]) and df.loc[3, "quotidien"] == 1.0
    assert df.loc[4, "quotidien"] == 0.0
    assert df.loc[0, "plus_2h"] == 1.0 and df.loc[3, "plus_2h"] == 0.0
    assert pd.isna(df.loc[3, "forme"]) and df.loc[1, "forme"] == 0.0
    assert df.loc[0, "forme_travail"] == 1.0 and df.loc[2, "forme_travail"] == 0.0
    assert df.loc[4, "moyen_1"] == 1.0 and pd.isna(df.loc[1, "moyen_1"])


def test_filtrer(df):
    sel = axe.filtrer(df, ["Germany"])
    assert set(sel["Country"]) == {"France", "Germany"}
    assert set(sel["Zone"]) == {"France", "Europe"}
    assert len(axe.filtrer(df, ["Germany"], situations=["Salariés"])) == 4
    assert len(axe.filtrer(df, ["Germany"], experiences=["0 à 4 ans"])) == 2


def test_part_et_tableau(df):
    sel = axe.filtrer(df, ["Germany"])
    france = sel[sel["Zone"] == "France"]
    assert axe.part(france, "utilise_ia") == (pytest.approx(2 / 3), 2, 3)
    assert axe.part(france.iloc[0:0], "utilise_ia") == (None, 0, 0)
    t = axe.tableau(sel, ["utilise_ia", "forme"])
    assert len(t) == 4
    assert set(t.columns) >= {"indicateur", "Zone", "part", "n", "base", "marge"}


def test_ecart_et_marge(df):
    sel = axe.filtrer(df, ["Germany"])
    e = axe.ecart(sel, "utilise_ia")
    assert e["ecart"] == pytest.approx(100 * (2 / 3 - 1))
    assert e["marge"] > 0
    assert axe.marge(0.5, 100) == pytest.approx(0.098, abs=1e-3)
    assert math.isnan(axe.marge(None, 0))


def test_par_pays_et_segments(df):
    sel = axe.filtrer(df, ["Germany"])
    pays = axe.par_pays(sel, "utilise_ia").set_index("pays")
    assert pays.loc["Allemagne", "part"] == 1.0 and bool(pays.loc["France", "france"])
    seg = axe.par_segment(sel, "utilise_ia", "Age")
    assert list(seg["segment"].unique()) == ["18-24 ans", "25-34 ans", "35-44 ans"]
    assert not seg["affiche"].any()  # tout est sous le seuil de 100 ici
    assert axe.ecarts_par_segment(sel, "utilise_ia", "Age").empty


def test_composition_et_repartition(df):
    sel = axe.filtrer(df, ["Germany"])
    standard = axe.europe_a_composition_francaise(sel, "utilise_ia", "Age")
    assert 0 <= standard <= 1
    rep = axe.repartition(sel, "LearnAI", axe.FORMATION_FR)
    france = rep[rep["Zone"] == "France"]
    assert france["part"].sum() == pytest.approx(1)
    assert list(france["reponse"]) == list(axe.FORMATION_FR.values())


def test_entonnoir_et_preuves(df):
    sel = axe.filtrer(df, ["Germany"])
    e = axe.entonnoir(sel).set_index("etape")
    assert e.iloc[0]["France"] == 4 and e.iloc[1]["France"] == 3
    preuves = axe.table_de_preuves(sel)
    assert list(preuves.columns) == ["test", "resultat", "tient"]
    assert len(preuves) >= 1


def test_formats_francais():
    assert axe.fr_pct(0.753) == "75 %"
    assert axe.fr_pct(None) == "—"
    assert axe.fr_pts(-6.84) == "−6,8 pts"
    assert axe.fr_n(5072) == "5 072"


def test_catalogue_complet():
    for code in axe.INDICATEURS:
        theme, libelle, base = axe.INDICATEURS[code]
        assert theme in {"Adoption", "Fréquence", "Formation"} and libelle and base
