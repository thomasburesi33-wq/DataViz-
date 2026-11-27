"""Tests de l'axe 4 (analysis/axe_4.py), sur des données inventées."""
import pandas as pd
import pytest

from analysis import accueil, axe_4


@pytest.fixture
def sel():
    n = 4
    df = pd.DataFrame({
        "Country": ["France", "France", "Germany", "Germany"],
        "Age": ["25-34 years old"] * n,
        "OrgSize": ["10,000 or more employees", "20 to 99 employees",
                    "10,000 or more employees", "Just me - I am a freelancer, sole proprietor, etc."],
        "Disruption": ["Plausible but wrong code;Missing context", "Missing context",
                       "Plausible but wrong code", None],
        "AIUse": ["My organization provides approved AI tools and guidance for how to use them",
                  "AI use is mostly optional and left up to individuals",
                  "My organization provides approved AI tools and guidance for how to use them",
                  "Not sure"],
    })
    for k in axe_4.TACHES:
        df[f"AIImpact_{k}"] = ["Very useful", "Not applicable", "Useful", None]
        df[f"AISat_{k}"] = ["Greatly improved", "Somewhat decreased", "No change", None]
    return accueil.filtrer(df, ["Germany"])


def test_utilite_base_avec_et_sans_non_applicable(sel):
    u = axe_4.utilite_par_tache(sel).set_index(["tache", "Zone"])
    assert u.loc[("Conception", "France"), "part"] == 0.5
    assert u.loc[("Conception", "France"), "base"] == 2
    u2 = axe_4.utilite_par_tache(sel, exclure_na=True).set_index(["tache", "Zone"])
    assert u2.loc[("Conception", "France"), "part"] == 1.0


def test_satisfaction(sel):
    s = axe_4.satisfaction_par_tache(sel, "France").set_index("tache")
    assert s.loc["Implémentation", "ameliore"] == 0.5
    assert s.loc["Implémentation", "degrade"] == 0.5


def test_erreurs_choix_multiples(sel):
    e = axe_4.erreurs_couteuses(sel).set_index(["erreur", "Zone"])
    assert e.loc[("Code plausible mais faux", "France"), "part"] == 0.5
    assert e.loc[("Contexte manquant", "France"), "n"] == 2
    assert e.loc[("Code plausible mais faux", "Europe"), "base"] == 1


def test_politique_par_taille_ecarte_independants(sel):
    p = axe_4.politique_par_taille(sel, "Europe").set_index(["taille", "politique"])
    assert p.loc[("1 000 salariés et plus", "Outils approuvés et consignes"), "base"] == 1
    assert p.loc[("Moins de 1 000 salariés", "Outils approuvés et consignes"), "base"] == 0


def test_indicateurs(sel):
    k = axe_4.indicateurs(sel)
    assert len(k) == 4 and k[0]["france"] == 0.5

