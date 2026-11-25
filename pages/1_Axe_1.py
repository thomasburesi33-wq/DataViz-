"""Page de l'axe 1 — Organisation du travail : uniquement de la présentation.

La logique est dans analysis/axe_1.py. Les clés de widgets de cet axe commencent par axe1_.
"""
import streamlit as st

st.set_page_config(page_title="Axe 1 · Organisation du travail", layout="wide")

from analysis import axe_1 as axe  # noqa: E402
from analysis import config  # noqa: E402
from ui import charts, common  # noqa: E402

# TODO responsable de l'axe : un titre qui dit ce que l'on découvre, pas le sujet.
st.title("Axe 1 — Organisation du travail")
st.caption(f"{config.SOURCE_LABEL} {config.MAIN_YEAR} · exemple de structure à remplacer")

survey = common.load_year(config.MAIN_YEAR)
population_sel, filters = common.population_filters(survey)

with st.sidebar:
    st.subheader("Filtres de l'axe")
    axis_values = st.multiselect(
        "Taille de l'entreprise", sorted(population_sel[axe.AXIS_FILTER].dropna().unique()),
        key="axe1_filter", help="Vide = pas de filtre")
    top = st.slider("Modalités affichées", 5, 30, 12, key="axe1_top")

selection = axe.filter_axis(population_sel, axis_values)
common.stop_if_empty(selection)

table = axe.main_table(selection)
respondents = selection[selection[axe.QUESTION].notna()]
if table.empty:
    st.info("Personne n'a répondu à cette question dans la sélection.")
else:
    common.show_figure(charts.barh_shares(table, "Mode de travail des répondants en poste", top=top))
    extra = "ayant répondu à la question sur le mode de travail"
    if axis_values:
        extra += " · Taille de l'entreprise : " + ", ".join(axis_values)
    common.show_population(respondents, filters, extra=extra)
    with st.expander("Voir la table"):
        st.dataframe(table, hide_index=True)

# --- Comparaison 2025 (optionnelle) : passe TOUJOURS par l'harmonisation ------------------
if st.toggle("Comparer avec 2025", key="axe1_compare_2025",
             help="Télécharge l'enquête 2025 au premier usage (~140 Mo)"):
    from analysis import harmonisation, indicators, population

    # Même population les deux années : le filtre « Rapport au code » n'existe pas en 2025.
    same = {"countries": filters["countries"], "employment": filters["employment"]}
    sel_2026 = axe.filter_axis(population.filter_population(survey, **same), axis_values)
    sel_2025 = axe.filter_axis(
        population.filter_population(common.load_2025_harmonised(), **same), axis_values)
    both = harmonisation.comparable(sel_2026, sel_2025, axe.QUESTION)
    for year, group in both.groupby("year"):
        st.markdown(f"**{year}**")
        common.show_figure(charts.barh_shares(
            indicators.share_single(group, axe.QUESTION), f"Mode de travail, {year}"))
        common.show_population(group.dropna(), {**same, "code_main": []}, year=year,
                               extra="ayant répondu à la question sur le mode de travail")
    st.caption("Correspondance RemoteWork (2025) → WorkSetting (2026) : "
               "voir docs/harmonisation_2025_2026.md. Le filtre « Rapport au code » "
               "n'existe pas en 2025 et n'est pas appliqué à cette comparaison.")
