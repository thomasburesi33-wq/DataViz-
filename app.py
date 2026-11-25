"""Tableau de bord principal : le message pour le commanditaire.

Lancer : uv run streamlit run app.py
Les cinq axes d'approfondissement sont dans pages/ (un fichier par axe).
"""
import streamlit as st

st.set_page_config(page_title="Stack Overflow 2026 · Tableau de bord", layout="wide")

from analysis import config, indicators  # noqa: E402  (set_page_config doit passer en premier)
from ui import charts, common  # noqa: E402

# TODO groupe : remplacer par LE message pour le commanditaire, en une phrase affirmative.
st.title("Message pour le commanditaire : à écrire")
st.caption(f"{config.SOURCE_LABEL} {config.MAIN_YEAR} · commanditaire : à définir "
           "(voir CADRAGE.md)")

survey = common.load_year(config.MAIN_YEAR)
selection, filters = common.population_filters(survey)
common.stop_if_empty(selection)

common.volunteer_notice()

# --- Bandeau d'indicateurs --------------------------------------------------------------
k = indicators.headline_kpis(selection)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Répondants", common.fmt(k["n_respondents"], "{:,}"))
c2.metric("Codent comme activité principale", common.fmt(k["share_code_main"], "{:.0%}"))
c3.metric("Expérience pro médiane", common.fmt(k["median_work_exp"], "{:.0f} ans"))
c4.metric("Rémunération annuelle médiane", common.fmt(k["median_comp_usd"], "{:,.0f} $"))
common.show_population(selection, filters)

# --- Figure-clé -------------------------------------------------------------------------
# TODO groupe : remplacer par la figure qui porte le message du tableau de bord.
st.subheader("Figure-clé (exemple à remplacer)")
column = "LanguagesHaveWorkedWith"
table = indicators.share_multi(selection, column)
respondents = selection[selection[column].notna()]
if table.empty:
    st.info("Personne n'a répondu à cette question dans la sélection.")
else:
    common.show_figure(charts.barh_shares(
        table, "Langages utilisés de façon intensive l'année passée"))
    common.show_population(respondents, filters,
                           extra="ayant répondu à la question sur les langages")
    with st.expander("Voir la table"):
        st.dataframe(table, hide_index=True)

# --- Accès aux cinq axes ----------------------------------------------------------------
st.subheader("Approfondir")
cols = st.columns(5)
for col, (page, label) in zip(cols, [
    ("pages/1_Axe_1.py", "Axe 1"),
    ("pages/2_Axe_2.py", "Axe 2"),
    ("pages/3_Axe_3.py", "Axe 3"),
    ("pages/4_Axe_4.py", "Axe 4"),
    ("pages/5_Axe_5.py", "Axe 5"),
]):
    col.page_link(page, label=label)
