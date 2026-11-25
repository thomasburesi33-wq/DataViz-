"""Page de l'axe 5 — Apprentissage : uniquement de la présentation.

La logique est dans analysis/axe_5.py. Les clés de widgets de cet axe commencent par axe5_.
"""
import streamlit as st

st.set_page_config(page_title="Axe 5 · Apprentissage", layout="wide")

from analysis import axe_5 as axe  # noqa: E402
from analysis import config  # noqa: E402
from ui import charts, common  # noqa: E402

# TODO responsable de l'axe : un titre qui dit ce que l'on découvre, pas le sujet.
st.title("Axe 5 — Apprentissage")
st.caption(f"{config.SOURCE_LABEL} {config.MAIN_YEAR} · exemple de structure à remplacer")

survey = common.load_year(config.MAIN_YEAR)
population_sel, filters = common.population_filters(survey)

with st.sidebar:
    st.subheader("Filtres de l'axe")
    axis_values = st.multiselect(
        "Tranche d'âge", sorted(population_sel[axe.AXIS_FILTER].dropna().unique()),
        key="axe5_filter", help="Vide = pas de filtre")
    top = st.slider("Modalités affichées", 5, 30, 12, key="axe5_top")

selection = axe.filter_axis(population_sel, axis_values)
common.stop_if_empty(selection)

table = axe.main_table(selection)
respondents = selection[selection[axe.QUESTION].notna()]
if table.empty:
    st.info("Personne n'a répondu à cette question dans la sélection.")
else:
    common.show_figure(charts.barh_shares(table, "Comment les répondants ont appris à coder l'année passée", top=top))
    extra = "ayant répondu à la question sur l'apprentissage"
    if axis_values:
        extra += " · Tranche d'âge : " + ", ".join(axis_values)
    common.show_population(respondents, filters, extra=extra)
    with st.expander("Voir la table"):
        st.dataframe(table, hide_index=True)
