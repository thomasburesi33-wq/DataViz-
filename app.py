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

# =====================================================================================
# Tableau de bord : la France face à ses voisins européens sur l'IA
# Question : les répondants vivant en France se distinguent-ils de leurs voisins
# européens dans leur rapport à l'IA, et sur quoi (usage, freins, confiance) ?
# =====================================================================================
import altair as alt  # noqa: E402  (fourni avec Streamlit, aucune dépendance à ajouter)

from analysis import accueil  # noqa: E402
from ui import common  # noqa: E402

st.divider()

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
        "Tranches d'âge", sorted(survey["Age"].dropna().unique()), default=[],
        key="accueil_ages", help="Vide = tous les âges",
    )

if not europe:
    st.warning("Choisissez au moins un pays européen dans la barre latérale.")
    st.stop()

# --- Calculs : tous dans analysis/accueil.py ---
selection = accueil.filtrer(survey, europe, ages)
tableau = accueil.tableau_france_europe(selection)
resume = accueil.ecarts(tableau)
vue_par_defaut = list(europe) == accueil.EUROPE_DEFAUT and not ages

n_fr = int((selection["Zone"] == "France").sum())
n_eu = int((selection["Zone"] == "Europe").sum())
pays_txt = ", ".join(accueil.NOMS_FR.get(c, c) for c in europe)
age_txt = "tous âges" if not ages else ", ".join(ages)
legende_source = (
    f"Source : enquête Stack Overflow 2026 · répondants volontaires vivant en France "
    f"(n = {common.fmt(n_fr, '{:,}')}) et dans {len(europe)} pays européens "
    f"(n = {common.fmt(n_eu, '{:,}')}) · {age_txt} · chaque part est calculée sur les "
    "répondants à la question (bases dans l'onglet Données). Non représentatif de "
    "l'ensemble des développeurs."
)

# --- Garde-fou : pas de figure sur un effectif trop faible ---
trop_petits = accueil.bases_insuffisantes(tableau)
if not trop_petits.empty:
    st.warning(
        f"Avec ces filtres, au moins un indicateur repose sur moins de "
        f"{accueil.MIN_REPONDANTS} répondants ({int(trop_petits['base'].min())} au plus "
        f"bas) : la marge d'erreur dépasserait ±10 points, trop pour comparer la France "
        "à l'Europe. Élargissez les tranches d'âge ou les pays."
    )
    st.stop()

constat, explorer, donnees_tab = st.tabs(["Le constat", "Explorer", "Données"])

# =====================================================================================
# Onglet 1 · Le constat : 4 indicateurs + la figure-clé
# =====================================================================================
with constat:
    for col, ligne in zip(st.columns(4), resume.itertuples()):
        col.metric(
            ligne.indicateur,
            f"{ligne.France:.0%}",
            delta=f"{ligne.ecart_points:+.1f} pts vs Europe".replace(".", ","),
            delta_color="off",
            help=f"Europe : {ligne.Europe:.0%}",
        )

    # Le titre n'affirme le constat que sur la population par défaut, où il a été vérifié ;
    # pour une autre sélection, il décrit ce que montre la figure.
    titre = (
        "En France, plus de réserves envers l'IA, mais autant de confiance chez ceux "
        "qui l'utilisent"
        if vue_par_defaut
        else "France et Europe : usage de l'IA, freins et confiance (sélection filtrée)"
    )

    # Figure en haltères : la France en couleur (le message), l'Europe en gris (le contexte).
    donnees = tableau.dropna(subset=["part"])
    ordre = [i[0] for i in accueil.INDICATEURS]
    couleurs = alt.Scale(domain=["France", "Europe"], range=["#257de0", "#a3a3a3"])
    y = alt.Y("indicateur:N", sort=ordre, title=None, axis=alt.Axis(labelLimit=320))
    x = alt.X("part:Q", title="Part des répondants",
              axis=alt.Axis(format="%", tickCount=6), scale=alt.Scale(zero=True, nice=True))
    infobulle = [
        alt.Tooltip("indicateur:N", title="Indicateur"),
        alt.Tooltip("Zone:N"),
        alt.Tooltip("part:Q", title="Part", format=".1%"),
        alt.Tooltip("n:Q", title="Répondants concernés"),
        alt.Tooltip("base:Q", title="Base (n)"),
        alt.Tooltip("base_texte:N", title="Base"),
    ]
    trait = alt.Chart(donnees).mark_line(color="#d9d9d9", strokeWidth=3).encode(
        x=x, y=y, detail="indicateur:N")
    points = alt.Chart(donnees).mark_circle(size=220, opacity=1).encode(
        x=x, y=y, tooltip=infobulle,
        color=alt.Color("Zone:N", scale=couleurs, legend=alt.Legend(title=None, orient="top")))

    # Valeurs au-dessus du point France, en dessous du point Europe : jamais superposées.
    def _valeurs(zone: str, decalage: int) -> alt.Chart:
        return alt.Chart(donnees).transform_filter(alt.datum.Zone == zone).mark_text(
            dy=decalage, fontSize=11, fontWeight="bold").encode(
            x=x, y=y, color=alt.Color("Zone:N", scale=couleurs, legend=None),
            text=alt.Text("part:Q", format=".0%"))

    st.altair_chart(
        (trait + points + _valeurs("France", -16) + _valeurs("Europe", 16))
        .properties(height=340, title=titre),
        width="stretch",
    )

    # Population étudiée sous la figure, recalculée selon les filtres.
    st.markdown(
        f"**👥 Population étudiée : {common.fmt(n_fr + n_eu, '{:,}')} répondants** "
        f"· France : **{common.fmt(n_fr, '{:,}')}** "
        f"· Europe : **{common.fmt(n_eu, '{:,}')}** ({pays_txt}) · Âge : {age_txt}"
    )
    st.caption(legende_source)

# =====================================================================================
# Onglet 2 · Explorer : un indicateur, pays par pays (graphique natif)
# =====================================================================================
with explorer:
    choix = st.selectbox("Indicateur à explorer", ordre, key="accueil_explorer")
    detail = accueil.par_pays(selection, choix)
    affiches = detail[detail["base"] >= accueil.MIN_REPONDANTS]
    st.subheader(f"{choix}, pays par pays")
    st.bar_chart(affiches.set_index("pays")["part"], horizontal=True,
                 x_label="Part des répondants", y_label="", color="#257de0")
    masques = detail[detail["base"] < accueil.MIN_REPONDANTS]
    if not masques.empty:
        st.info("Masqués car sous " + str(accueil.MIN_REPONDANTS) + " répondants : "
                + ", ".join(f"{r.pays} (n = {r.base})" for r in masques.itertuples()))
    st.caption(
        "Source : enquête Stack Overflow 2026 · répondants volontaires ayant répondu à la "
        f"question, par pays ({age_txt}) : "
        + ", ".join(f"{r.pays} n = {r.base}" for r in affiches.itertuples())
        + ". Non représentatif de l'ensemble des développeurs."
    )

# =====================================================================================
# Onglet 3 · Données : la table derrière la figure-clé
# =====================================================================================
with donnees_tab:
    st.markdown("La table derrière la figure-clé : une ligne par indicateur et par zone.")
    st.dataframe(
        tableau.assign(marge=tableau["base"].map(accueil.marge_erreur))[
            ["indicateur", "Zone", "part", "n", "base", "marge", "base_texte"]],
        hide_index=True,
        column_config={
            "part": st.column_config.NumberColumn("Part", format="percent"),
            "n": st.column_config.NumberColumn("Ont coché la réponse"),
            "base": st.column_config.NumberColumn("Base (répondants à la question)"),
            "marge": st.column_config.NumberColumn("Marge d'erreur max (±)",
                                                   format="percent"),
            "base_texte": "Qui a répondu",
        },
    )
    st.caption(legende_source)
