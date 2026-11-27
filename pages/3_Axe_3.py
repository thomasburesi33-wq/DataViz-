"""Axe 3 — Outils et modèles : quoi fournir ? (présentation uniquement).

La France est comparée aux 8 pays européens retenus par le groupe ; toute la logique
vit dans analysis/axe_3.py, cette page affiche les tables renvoyées par l'analyse
et rappelle la population sous chaque figure.
"""
from __future__ import annotations

import altair as alt  # fourni avec Streamlit, comme dans app.py : aucune dépendance à ajouter
import streamlit as st

from analysis import accueil, axe_3, config, load
from ui import common

st.title("Axe 3 · Outils et modèles : quoi fournir ?")
st.markdown(
    """
**Question de la DSI :** quels assistants de code et quels fournisseurs de modèles
sont réellement utilisés ? Existe-t-il une option européenne crédible (Mistral) ?
Pourquoi les développeurs changent-ils d'outil ?

La **France** (bleu) est comparée à ses **8 voisins européens** (orange : Allemagne,
Royaume-Uni, Pays-Bas, Espagne, Italie, Pologne, Suède, Suisse). Les parts sont
exprimées parmi les répondants ayant répondu à chaque question ; l'option
européenne Mistral est repérée par (UE).
"""
)

survey = common.load_year(config.MAIN_YEAR)

# --- Filtres : pays de comparaison (choix du groupe) + poste, propre à l'axe ---
with st.sidebar:
    st.subheader("Population")
    europe = st.multiselect(
        "Pays européens comparés à la France",
        accueil.EUROPE_DEFAUT, default=accueil.EUROPE_DEFAUT,
        format_func=lambda c: accueil.NOMS_FR.get(c, c),
        key="axe3_europe", help="Choix limité aux 8 pays européens de comparaison",
    )
    st.subheader("Filtre de l'axe")
    roles = st.multiselect(
        "Poste", sorted(survey["Role"].dropna().unique()),
        key="axe3_roles", help="Vide = tous les postes",
    )

if not europe:
    st.warning("Choisissez au moins un pays européen dans la barre latérale.")
    st.stop()

selection = axe_3.filtrer_population(survey, europe, roles)
common.stop_if_empty(selection)
france = selection[selection["Zone"] == "France"]
europe_sel = selection[selection["Zone"] == "Europe"]
if france.empty:
    st.warning("Aucun répondant en France ne correspond à ces filtres.")
    st.stop()

# --- Population sous chaque figure : qui, quelle année, combien de répondants ---

def _show_population(df_zone, zone: str, extra: str) -> None:
    """Affiche la population d'une zone sous une figure, avec avertissement si fragile."""
    who = ["France"] if zone == "France" else [accueil.NOMS_FR.get(c, c) for c in europe]
    if roles:
        extra = f"poste : {', '.join(roles)} · {extra}"
    common.show_population(df_zone, {"countries": who, "code_main": [], "employment": []},
                           extra=extra)

def _ecart(part_fr: float | None, part_eu: float | None) -> str | None:
    """Écart France − Europe en points de pourcentage, pour st.metric."""
    if part_fr is None or part_eu is None:
        return None
    return f"{100 * (part_fr - part_eu):+.1f} pts vs Europe".replace(".", ",")

def _figure_compare(donnees, titre: str, xlabel: str = "Part des répondants") -> None:
    """Barres horizontales groupées : France en bleu, Europe en orange, côte à côte.

    La hauteur est fixée PAR OPTION (alt.Step) : les deux barres d'une option ont
    toujours la place d'être séparées, quelle que soit la taille de la fenêtre.
    La table vient de analysis/axe_3.py (colonnes option, share, n, base, Zone) ;
    cette fonction ne calcule rien, elle ne fait qu'afficher.
    """
    couleurs = alt.Scale(domain=["France", "Europe"], range=["#257de0", "#f47230"])
    chart = (
        alt.Chart(donnees)
        .mark_bar()
        .encode(
            y=alt.Y("option:N", title=None, axis=alt.Axis(labelLimit=280),
                    sort=alt.EncodingSortField(field="share", op="max",
                                               order="descending")),
            yOffset=alt.YOffset("Zone:N"),
            x=alt.X("share:Q", title=xlabel, axis=alt.Axis(format="%", tickCount=6)),
            color=alt.Color("Zone:N", scale=couleurs,
                            legend=alt.Legend(title=None, orient="top")),
            tooltip=[
                alt.Tooltip("option:N", title="Option"),
                alt.Tooltip("Zone:N"),
                alt.Tooltip("share:Q", title="Part", format=".1%"),
                alt.Tooltip("n:Q", title="Répondants"),
                alt.Tooltip("base:Q", title="Base (n)"),
            ],
        )
        .properties(title=titre, height=alt.Step(30))
    )
    # Colonnes latérales vides : le graphe reste compact et centré, au lieu de
    # s'étirer sur toute la largeur de la page.
    _, centre, _ = st.columns([1, 8, 1])
    with centre:
        st.altair_chart(chart, width="stretch")

# --- Bandeau : la France face à l'Europe sur les chiffres du choix des licences ---
k_fr, k_eu = axe_3.kpis(france), axe_3.kpis(europe_sel)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Assistant n°1 en France", k_fr["top_agent"] or "—",
            common.fmt(k_fr["top_agent_share"], "{:.0%}"), delta_color="off",
            help=f"Europe : {k_eu['top_agent'] or '—'} "
                 f"({common.fmt(k_eu['top_agent_share'], '{:.0%}')})")
col2.metric("Fournisseur n°1 en France", k_fr["top_llm"] or "—",
            common.fmt(k_fr["top_llm_share"], "{:.0%}"), delta_color="off",
            help=f"Europe : {k_eu['top_llm'] or '—'} "
                 f"({common.fmt(k_eu['top_llm_share'], '{:.0%}')})")
col3.metric("Ont changé d'outil IA (France)",
            common.fmt(k_fr["share_switched"], "{:.0%}"),
            _ecart(k_fr["share_switched"], k_eu["share_switched"]), delta_color="off")
m_fr, m_eu = k_fr["mistral_llm"], k_eu["mistral_llm"]
col4.metric("Mistral AI (UE) — France",
            "—" if m_fr is None else common.fmt(m_fr[1], "{:.0%}"),
            None if m_fr is None else _ecart(m_fr[1], None if m_eu is None else m_eu[1]),
            delta_color="off")

st.divider()

# --- Figure 1 : assistants de code, France face à l'Europe ---
st.subheader("Quels assistants de code fournir ?")
agents_comp = axe_3.code_agents_compare(selection)
agents_fig = agents_comp.assign(option=agents_comp["option"].replace(
    {axe_3.EUROPEAN_AGENT: f"{axe_3.EUROPEAN_AGENT} (UE)"}))
_figure_compare(agents_fig, "Assistants de code utilisés dans l'année écoulée "
                            "(choix multiples)")
col_fr, col_eu = st.columns(2)
with col_fr:
    _show_population(france[france[axe_3.QUESTION_AGENTS].notna()], "France",
                     "ayant répondu à la question sur les assistants de code")
with col_eu:
    _show_population(europe_sel[europe_sel[axe_3.QUESTION_AGENTS].notna()], "Europe",
                     "ayant répondu à la question sur les assistants de code")
row = axe_3.code_agents_table(france)
row = row.loc[row["option"] == axe_3.EUROPEAN_AGENT]
if not row.empty:
    n_mistral_vibe = int(row["n"].iloc[0])
    message = (f"⚠️ {axe_3.EUROPEAN_AGENT} : n = {n_mistral_vibe} répondants en France "
               "— ordre de grandeur indicatif, à ne pas sur-interpréter.")
    (st.warning if n_mistral_vibe < config.MIN_N else st.caption)(message)

# --- Figure 2 : fournisseurs de modèles, France face à l'Europe ---
st.subheader("Quels fournisseurs de modèles ?")
llms_comp = axe_3.llm_vendors_compare(selection)
llms_fig = llms_comp.assign(option=llms_comp["option"].replace(
    {axe_3.EUROPEAN_LLM: f"{axe_3.EUROPEAN_LLM} (UE)"}))
_figure_compare(llms_fig, "Fournisseurs de modèles IA utilisés dans l'année écoulée "
                          "(choix multiples)")
col_fr, col_eu = st.columns(2)
with col_fr:
    _show_population(france[france[axe_3.QUESTION_LLMS].notna()], "France",
                     "ayant répondu à la question sur les fournisseurs de modèles")
with col_eu:
    _show_population(europe_sel[europe_sel[axe_3.QUESTION_LLMS].notna()], "Europe",
                     "ayant répondu à la question sur les fournisseurs de modèles")

# --- Figure 3 : pourquoi changer d'outil, France face à l'Europe ---
st.subheader("Pourquoi les développeurs changent-ils d'outil ?")
REASONS_FR = {
    "better output quality": "Meilleure qualité des résultats",
    "my organization required or recommended a different tool":
        "Mon entreprise a imposé ou recommandé un autre outil",
    "better integration with my workflow or development environment":
        "Meilleure intégration à mon flux de travail",
    "lower cost": "Coût plus faible",
    "another reason (write in)": "Autre raison",
    "the previous tool became too expensive, limited, or unavailable":
        "L'outil précédent est devenu trop cher, limité ou indisponible",
    "better support for agents, automation, or coding workflows":
        "Meilleur support des agents et de l'automatisation",
    "access to a preferred model or provider": "Accès à un modèle ou fournisseur préféré",
    "better security, privacy, or compliance": "Meilleure sécurité, confidentialité, conformité",
    "for a specific feature": "Pour une fonctionnalité précise",
}
switch_comp = axe_3.switch_compare(selection)
switch_fig = switch_comp.assign(
    option=switch_comp["option"].map(REASONS_FR).fillna(switch_comp["option"]))
if switch_fig.empty:
    st.info("Aucun répondant n'a changé d'outil IA dans cette population.")
else:
    _figure_compare(switch_fig, "Raisons du changement d'outil IA, parmi ceux qui ont "
                                "changé", xlabel="Part des répondants ayant changé d'outil")
col_fr, col_eu = st.columns(2)
with col_fr:
    _show_population(france[france[axe_3.QUESTION_SWITCH].str.startswith(
        axe_3.SWITCH_YES, na=False)], "France", "ayant changé d'outil IA dans l'année")
with col_eu:
    _show_population(europe_sel[europe_sel[axe_3.QUESTION_SWITCH].str.startswith(
        axe_3.SWITCH_YES, na=False)], "Europe", "ayant changé d'outil IA dans l'année")

# --- Lecture pour la DSI (calculée sur la sélection affichée) ---
st.subheader("Lecture pour la DSI")
switch_fr = axe_3.switch_table(france).assign(
    option=lambda t: t["option"].map(REASONS_FR).fillna(t["option"]))
lignes = []
if k_fr["top_agent"] and k_eu["top_agent"]:
    lignes.append(
        f"- **Licences prioritaires** : {k_fr['top_agent']} "
        f"({common.fmt(k_fr['top_agent_share'], '{:.0%}')} en France) et "
        f"{k_eu['top_agent']} côté européen concentrent l'usage des assistants "
        "de code — ce sont les outils à contractualiser en premier.")
if m_fr and m_eu:
    lignes.append(
        f"- **Option européenne** : {axe_3.EUROPEAN_LLM} est utilisé par "
        f"{common.fmt(m_fr[1], '{:.0%}')} des répondants français contre "
        f"{common.fmt(m_eu[1], '{:.0%}')} chez les voisins — la demande existe en "
        "France, ce qui rend crédible une politique « européenne d'abord » "
        "accompagnée, plutôt qu'une substitution imposée.")
if k_fr["share_switched"] is not None and not switch_fr.empty:
    lignes.append(
        f"- **Fidélité faible** : {common.fmt(k_fr['share_switched'], '{:.0%}')} des "
        f"utilisateurs d'IA français ont changé d'outil dans l'année, d'abord pour "
        f"« {switch_fr['option'].iloc[0].lower()} » — prévoir des contrats "
        "réévaluables plutôt que des engagements longs.")
st.markdown("\n".join(lignes) if lignes else
            "Sélection trop restreinte pour dégager une lecture.")

with st.expander("Détail des données et questions de l'enquête"):
    schema = common.load_schema(config.MAIN_YEAR)
    for col in (axe_3.QUESTION_AGENTS, axe_3.QUESTION_LLMS, axe_3.QUESTION_SWITCH):
        st.caption(f"`{col}` — {load.question_text(schema, col)}")
    fmt_share = {"share": st.column_config.NumberColumn("Part", format="percent")}
    st.markdown("**Assistants de code** — une ligne par option et par zone")
    st.dataframe(agents_comp, hide_index=True, column_config=fmt_share)
    st.markdown("**Fournisseurs de modèles** — une ligne par option et par zone")
    st.dataframe(llms_comp, hide_index=True, column_config=fmt_share)
    st.markdown("**Raisons du changement d'outil** — une ligne par raison et par zone")
    st.dataframe(switch_comp, hide_index=True, column_config=fmt_share)

common.volunteer_notice()