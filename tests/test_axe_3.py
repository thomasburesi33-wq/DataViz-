"""Tests de l'axe 3 (analysis/axe_3.py), sur des données inventées."""
import pandas as pd
import pytest

from analysis import axe_3

@pytest.fixture
def df():
    return pd.DataFrame({
        "Country": ["France", "Germany", "France", "Spain", "France", "Japan"],
        "Role": ["Developer, full-stack", "Developer, back-end", "Student",
                 "Developer, full-stack", "Student", "Developer, back-end"],
        "AICodeAgentHaveWorkedWith": [
            "Claude Code;GitHub Copilot", "GitHub Copilot", None,
            "Claude Code;Mistral Vibe", "Mistral Vibe", "GitHub Copilot",
        ],
        "LLMHaveWorkedWith": [
            "Anthropic;OpenAI", "OpenAI", None,
            "Anthropic;Mistral AI", "Mistral AI", "OpenAI",
        ],
        "AIToolSwitch": [
            "Yes — better output quality", "No", None,
            "Yes — lower cost", axe_3.SWITCH_NA,
            "Yes — better output quality",
        ],
    })

@pytest.fixture
def sel(df):
    """La sélection France / Europe utilisée par les fonctions de comparaison."""
    return axe_3.filtrer_population(df, ["Germany", "Spain"])

def test_filter_axis_vide_signifie_pas_de_filtre(df):
    assert len(axe_3.filter_axis(df, [])) == len(df)
    roles = axe_3.filter_axis(df, ["Student"])
    assert set(roles["Role"]) == {"Student"}

def test_filtrer_population_france_face_a_leurope(df):
    sel = axe_3.filtrer_population(df, ["Germany", "Spain"])
    assert set(sel["Zone"]) == {"France", "Europe"}
    assert set(sel["Country"]) == {"France", "Germany", "Spain"}
    # Le Japon n'est pas dans la comparaison, quels que soient les filtres.
    assert "Japan" not in set(axe_3.filtrer_population(df)["Country"])
    assert set(axe_3.filtrer_population(df, ["Germany"], ["Student"])["Role"]) == {"Student"}

def test_code_agents_table_choix_multiples(df):
    table = axe_3.code_agents_table(df).set_index("option")
    assert table.loc["GitHub Copilot", "n"] == 3
    assert table.loc["GitHub Copilot", "base"] == 5  # les réponses manquantes sont exclues
    assert table.loc["Mistral Vibe", "share"] == pytest.approx(2 / 5)
    assert table["share"].sum() > 1  # choix multiples

def test_switch_table_ne_garde_que_les_raisons(df):
    table = axe_3.switch_table(df)
    assert table["base"].iloc[0] == 3          # « No » et « Not applicable » exclus
    assert set(table["option"]) == {"better output quality", "lower cost"}
    assert table.set_index("option").loc["better output quality", "share"] == \
        pytest.approx(2 / 3)

def test_switch_table_sur_selection_vide(df):
    assert axe_3.switch_table(df.iloc[0:0]).empty

def test_compare_empile_france_et_europe(sel):
    table = axe_3.code_agents_compare(sel)
    assert set(table["Zone"]) == {"France", "Europe"}
    # Chaque option est présente pour les deux zones : une seule figure groupée suffit.
    assert table.groupby("option")["Zone"].nunique().eq(2).all()
    copilot = table.set_index(["option", "Zone"]).loc[("GitHub Copilot", "France")]
    assert copilot["n"] == 1 and copilot["base"] == 3

def test_compare_switch_par_zone(sel):
    table = axe_3.switch_compare(sel)
    assert set(table["Zone"]) == {"France", "Europe"}
    assert set(table["option"]) == {"better output quality", "lower cost"}

def test_compare_sur_selection_vide(sel):
    vide = axe_3.filtrer_population(sel.iloc[0:0].drop(columns=["Zone"]))
    assert axe_3.code_agents_compare(vide).empty

def test_kpis(df):
    k = axe_3.kpis(df)
    assert k["top_agent"] == "GitHub Copilot"
    assert k["top_llm"] == "OpenAI"
    assert k["mistral_agent"] == (2, pytest.approx(2 / 5))
    assert k["mistral_llm"] == (2, pytest.approx(2 / 5))
    assert k["n_switched"] == 3
    assert k["switch_base"] == 4               # « Not applicable » exclu de la base
    assert k["share_switched"] == pytest.approx(3 / 4)

def test_kpis_sur_selection_vide(df):
    k = axe_3.kpis(df.iloc[0:0])
    assert k["top_agent"] is None and k["mistral_llm"] is None
    assert k["share_switched"] is None and k["switch_base"] == 0