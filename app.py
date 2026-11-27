"""Page principale : le sujet de l'analyse et sa source."""
import streamlit as st

st.set_page_config(page_title="IA et développeurs · DSI", layout="wide")

# --- Sujet de l'analyse ---
st.title("Quelle politique d'usage de l'IA pour nos développeurs ?")

st.markdown(
    """
**Commanditaire :** la DSI d'un grand groupe industriel français, présent en Europe
et engagé dans une démarche RSE.

**Sa question :** quels outils d'IA autoriser ou fournir à ses développeurs, pour quelles
tâches, avec quel accompagnement, et comment concilier cela avec ses engagements RSE ?

**Notre analyse :** comparer les répondants vivant en France à ceux de pays européens
voisins : usage de l'IA, freins, confiance, outils, impact sur le travail et politiques
des entreprises.
"""
)

# --- Source des données ---
st.subheader("Source")
st.markdown(
    """
- **Enquête Stack Overflow 2026** : [restitution officielle](https://survey.stackoverflow.co/2026)
- Données brutes : archive officielle
  [StackExchange/Survey](https://github.com/StackExchange/Survey), dossier `packages/archive/2026`
  (`survey_results_public.csv` et `survey_results_schema.csv`)
"""
)

# Tableau de bord : la France face à ses 8 voisins européens les plus représentéssur l'IA
# Question : les répondants vivant en France se distinguent-ils de leurs voisins
# européens dans leur rapport à l'IA, et sur quoi (usage, freins, confiance) ?

import altair as alt  # noqa: E402  (fourni avec Streamlit, aucune dépendance à ajouter)
import pandas as pd  # noqa: E402

from analysis import accueil  # noqa: E402
from ui import common  # noqa: E402

st.divider()
st.header("La France face à ses voisins européens")

survey = common.load_year(2026)  # lecture mise en cache, téléchargée si absente

# --- Filtres interactifs (barre latérale) ---
with st.sidebar:
    st.subheader("Filtres")
    # Seuls les 8 pays européens de comparaison sont proposés (choix du groupe).
    europe = st.multiselect(
        "Pays européens comparés à la France",
        accueil.EUROPE_DEFAUT,
        default=accueil.EUROPE_DEFAUT,
        format_func=lambda c: accueil.NOMS_FR.get(c, c),
        key="accueil_europe",
        help="Choix limité aux 8 pays européens de comparaison",
    )
    ages = st.multiselect(
        "Tranches d'âge", sorted(survey["Age"].dropna().unique()),
        key="accueil_ages", help="Vide = tous les âges",
    )

if not europe:
    st.warning("Choisissez au moins un pays européen dans la barre latérale.")
    st.stop()

selection = accueil.filtrer(survey, europe, ages)
tableau = accueil.tableau_france_europe(selection)
resume = accueil.ecarts(tableau)

# --- Bandeau : 4 chiffres clés (France, écart avec l'Europe) ---
for col, ligne in zip(st.columns(4), resume.itertuples()):
    col.metric(
        ligne.indicateur,
        "—" if pd.isna(ligne.France) else f"{ligne.France:.0%}",
        delta=None if pd.isna(ligne.ecart_points)
        else f"{ligne.ecart_points:+.1f} pts vs Europe".replace(".", ","),
        delta_color="off",
        help="Europe : " + ("—" if pd.isna(ligne.Europe) else f"{ligne.Europe:.0%}"),
    )

# --- Figure en haltères : un point France, un point Europe, reliés par un trait ---
donnees = tableau.dropna(subset=["part"])
ordre = [i[0] for i in accueil.INDICATEURS]
couleurs = alt.Scale(domain=["France", "Europe"], range=["#257de0", "#f47230"])
y = alt.Y("indicateur:N", sort=ordre, title=None, axis=alt.Axis(labelLimit=320))
x = alt.X("part:Q", title="Part des répondants", axis=alt.Axis(format="%", tickCount=6),
          scale=alt.Scale(zero=True, nice=True))
infobulle = [
    alt.Tooltip("indicateur:N", title="Indicateur"),
    alt.Tooltip("Zone:N"),
    alt.Tooltip("part:Q", title="Part", format=".1%"),
    alt.Tooltip("n:Q", title="Répondants concernés"),
    alt.Tooltip("base:Q", title="Base (n)"),
    alt.Tooltip("base_texte:N", title="Base"),
]
trait = alt.Chart(donnees).mark_line(color="#c2c2c2", strokeWidth=3).encode(
    x=x, y=y, detail="indicateur:N")
points = alt.Chart(donnees).mark_circle(size=220, opacity=1).encode(
    x=x, y=y, color=alt.Color("Zone:N", scale=couleurs, legend=alt.Legend(
        title=None, orient="top")), tooltip=infobulle)
# Valeurs au-dessus du point France, en dessous du point Europe : jamais superposées.
def _valeurs(zone: str, decalage: int) -> alt.Chart:
    return alt.Chart(donnees).transform_filter(alt.datum.Zone == zone).mark_text(
        dy=decalage, fontSize=11, fontWeight="bold").encode(
        x=x, y=y, color=alt.Color("Zone:N", scale=couleurs, legend=None),
        text=alt.Text("part:Q", format=".0%"))


valeurs = _valeurs("France", -16) + _valeurs("Europe", 16)
st.altair_chart(
    (trait + points + valeurs).properties(
        height=340,
        title="En France, plus de réserves envers l'IA, mais autant de confiance chez ceux "
              "qui l'utilisent",
    ),
    width="stretch",
)

# --- Population étudiée, sous la figure : recalculée à chaque changement de filtre ---
n_fr = int((selection["Zone"] == "France").sum())
n_eu = int((selection["Zone"] == "Europe").sum())
pays_txt = ", ".join(accueil.NOMS_FR.get(c, c) for c in europe)
age_txt = "tous âges" if not ages else ", ".join(ages)
st.markdown(
    f"**👥 Population étudiée : {common.fmt(n_fr + n_eu, '{:,}')} répondants** "
    f"· France : **{common.fmt(n_fr, '{:,}')}** "
    f"· Europe : **{common.fmt(n_eu, '{:,}')}** ({pays_txt}) · Âge : {age_txt}"
)
bases = " · ".join(
    f"{l.indicateur} : {l.n_fr} / {l.n_eu}"
    for l in tableau.pivot(index="indicateur", columns="Zone", values="base")
    .rename(columns={"France": "n_fr", "Europe": "n_eu"})
    .reindex([i[0] for i in accueil.INDICATEURS]).reset_index().itertuples()
)
st.caption(
    f"Population : répondants volontaires à l'enquête Stack Overflow 2026, non "
    f"représentatifs de l'ensemble des développeurs. Répondants à chaque question "
    f"(France / Europe) : {bases}."
)
if min(tableau["base"]) < 30:
    st.warning("Moins de 30 répondants pour au moins un indicateur : résultat fragile.")
with st.expander("Détail des bases par indicateur"):
    st.dataframe(
        tableau[["indicateur", "Zone", "part", "n", "base", "base_texte"]],
        hide_index=True,
        column_config={"part": st.column_config.NumberColumn("Part", format="percent")},
    )
