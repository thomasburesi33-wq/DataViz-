"""Tests de la logique d'analyse : aucune dépendance à Streamlit ni aux vraies données."""
import math

import pandas as pd
import pytest

from analysis import harmonisation, indicators, population


def test_empty_filter_means_no_filter(survey):
    assert len(population.filter_population(survey, [], [], [])) == len(survey)


def test_filter_population(survey):
    fr = population.filter_population(survey, countries=["France"])
    assert set(fr["Country"]) == {"France"}
    assert len(fr) == 4


def test_population_caption_mentions_year_and_n(survey):
    fr = population.filter_population(survey, countries=["France"])
    pop = population.describe_population(fr, 2026, countries=["France"])
    text = population.population_caption(pop)
    assert "2026" in text and "France" in text and "n = 4" in text
    assert pop.is_small


def test_share_single_base_excludes_missing(survey):
    table = indicators.share_single(survey, "WorkSetting")
    assert table["base"].iloc[0] == 4
    assert table.set_index("option").loc["Remote", "share"] == pytest.approx(0.75)


def test_share_multi_counts_each_option(survey):
    table = indicators.share_multi(survey, "LanguagesHaveWorkedWith").set_index("option")
    assert table.loc["Python", "n"] == 3
    assert table.loc["Python", "base"] == 4
    assert table["share"].sum() > 1  # choix multiples : les parts ne somment pas à 1


def test_shares_on_empty_selection(survey):
    empty = survey.iloc[0:0]
    assert indicators.share_single(empty, "WorkSetting").empty
    assert indicators.share_multi(empty, "LanguagesHaveWorkedWith").empty


def test_median_by_hides_small_groups(survey):
    table = indicators.median_by(survey, "ConvertedCompYearly", "OrgSize", min_n=2)
    small = table.set_index("group")
    assert small.loc["20 to 99 employees", "median"] == 60000
    assert math.isnan(small.loc["Less than 20 employees", "median"])


def test_headline_kpis_survive_empty_selection(survey):
    k = indicators.headline_kpis(survey.iloc[0:0])
    assert k["n_respondents"] == 0
    assert k["share_code_main"] is None and k["median_comp_usd"] is None


def test_harmonise_2025_renames_and_excludes(survey):
    raw_2025 = pd.DataFrame({"RemoteWork": ["Remote", "In-person"],
                             "Age": ["25-34 years old", "18-24 years old"],
                             "MainBranch": ["x", "y"]})
    h = harmonisation.harmonise_2025(raw_2025)
    assert "WorkSetting" in h.columns and "MainBranch" not in h.columns
    assert set(h["year"]) == {2025}
    both = harmonisation.comparable(survey, h, "Age")
    assert "Under 18 years old" not in set(both["Age"])


def test_not_comparable_column_is_refused(survey):
    with pytest.raises(ValueError):
        harmonisation.comparable(survey, survey, "AISelect")


def test_analysis_never_imports_streamlit():
    from pathlib import Path
    for file in (Path(__file__).parent.parent / "analysis").glob("*.py"):
        assert "import streamlit" not in file.read_text(encoding="utf-8"), file
