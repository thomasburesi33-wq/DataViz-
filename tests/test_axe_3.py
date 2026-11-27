"""Tests de l'axe 3 (analysis/axe_3.py), sur des données inventées."""
import pandas as pd
import pytest

from analysis import axe_3

@pytest.fixture
def df():
    return pd.DataFrame({
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

def test_filter_axis_vide_signifie_pas_de_filtre(df):
    assert len(axe_3.filter_axis(df, [])) == len(df)
    roles = axe_3.filter_axis(df, ["Student"])
    assert set(roles["Role"]) == {"Student"}

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