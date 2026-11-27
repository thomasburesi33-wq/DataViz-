"""Tests de la figure de la page principale (analysis/accueil.py), sur des données inventées."""
import pandas as pd
import pytest

from analysis import accueil


@pytest.fixture
def df():
    return pd.DataFrame({
        "Country": ["France", "France", "France", "Germany", "Germany", "Japan"],
        "Age": ["25-34 years old"] * 3 + ["35-44 years old"] * 2 + ["25-34 years old"],
        "AISelect": ["I don’t use AI tools", "General-purpose AI chat tools", None,
                     "I don’t use AI tools", "General-purpose AI chat tools", "x"],
        "AIAvoid": ["Environmental concerns;Moral or ethical concerns", None, None,
                    "I do not avoid using AI at work or school", None, None],
        "AITrust": [None, "I trust it when I can easily verify the output", None,
                    None, "I do not trust it for most work tasks", None],
    })


def test_filtrer_garde_france_et_europe(df):
    sel = accueil.filtrer(df, ["Germany"])
    assert set(sel["Country"]) == {"France", "Germany"}
    assert set(sel["Zone"]) == {"France", "Europe"}
    assert len(accueil.filtrer(df, ["Germany"], ["35-44 years old"])) == 2


def test_part_base_et_choix_multiples(df):
    fr = df[df["Country"] == "France"]
    assert accueil.part(fr, "AISelect", "I don’t use AI tools") == (0.5, 1, 2)
    assert accueil.part(fr, "AIAvoid", "Environmental concerns") == (1.0, 1, 1)
    assert accueil.part(fr.iloc[0:0], "AISelect", "x") == (None, 0, 0)


def test_tableau_et_ecarts(df):
    t = accueil.tableau_france_europe(accueil.filtrer(df, ["Germany"]))
    assert len(t) == 2 * len(accueil.INDICATEURS)
    e = accueil.ecarts(t).set_index("indicateur")
    assert e.loc["N'utilisent pas l'IA au travail", "ecart_points"] == pytest.approx(0)
    assert e.loc["N'ont aucune réserve envers l'IA", "Europe"] == pytest.approx(1)


def test_par_pays(df):
    t = accueil.par_pays(accueil.filtrer(df, ["Germany"]),
                         "N'utilisent pas l'IA au travail").set_index("pays")
    assert set(t.index) == {"France", "Allemagne"}
    assert t.loc["France", "base"] == 2 and t.loc["France", "part"] == 0.5


def test_seuil_et_marge(df):
    t = accueil.tableau_france_europe(accueil.filtrer(df, ["Germany"]))
    assert len(accueil.bases_insuffisantes(t)) == len(t)  # tout est sous 100 ici
    assert accueil.marge_erreur(100) == 0.1
