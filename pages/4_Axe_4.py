"""Axe 4 — Usages, impact et organisation : uniquement de la présentation.

Question de la DSI : pour quelles tâches l'IA est-elle utile, à quel prix en erreurs,
et comment les entreprises comparables l'encadrent-elles ?
La logique est dans analysis/axe_4.py. Les clés de widgets de cet axe commencent par axe4_.
"""
import streamlit as st

st.set_page_config(page_title="Axe 4 · Usages, impact et organisation", layout="wide")

import textwrap  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import PercentFormatter  # noqa: E402

from analysis import accueil, axe_4  # noqa: E402
from ui import common  # noqa: E402

FRANCE_COULEUR = "#257de0"  # le message
EUROPE_COULEUR = "#f47230"  # Europe en orange

st.title("Axe 4 · Usages, impact et organisation")
st.caption("Pour quelles tâches l'IA est-elle utile, à quel prix en erreurs, et comment "
           "les entreprises comparables l'encadrent-elles ? · Enquête Stack Overflow 2026")

survey = common.load_year(2026)

# --- Filtres (barre latérale), chacun avec sa valeur par défaut ---
with st.sidebar:
    st.subheader("Filtres de l'axe 4")
    europe = st.multiselect(
        "Pays européens comparés à la France", accueil.EUROPE_DEFAUT,
        default=accueil.EUROPE_DEFAUT, format_func=lambda c: accueil.NOMS_FR.get(c, c),
        key="axe4_europe")
    ages = st.multiselect("Tranches d'âge", sorted(survey["Age"].dropna().unique()),
                          default=[], key="axe4_ages", help="Vide = tous les âges")
    exclure_na = st.toggle(
        "Exclure « Non applicable » de la base", value=False, key="axe4_na",
        help="Par défaut, la base compte tous les répondants à la question "
             "(voir DECISIONS.md).")

if not europe:
    st.warning("Choisissez au moins un pays européen dans la barre latérale.")
    st.stop()

# --- Calculs : tous dans analysis/axe_4.py ---
selection = accueil.filtrer(survey, europe, ages)
utilite = axe_4.utilite_par_tache(selection, exclure_na)
vue_par_defaut = list(europe) == accueil.EUROPE_DEFAUT and not ages and not exclure_na

n_fr = int((selection["Zone"] == "France").sum())
n_eu = int((selection["Zone"] == "Europe").sum())
filtres_txt = "tous âges" if not ages else ", ".join(ages)


def legende(question: str, base_fr: int, base_eu: int | None = None) -> None:
    """Légende-source sous chaque figure : source, population, dénominateur."""
    eu = "" if base_eu is None else f" et dans {len(europe)} pays européens (n = {base_eu})"
    st.caption(
        f"Source : enquête Stack Overflow 2026 · répondants volontaires vivant en France "
        f"(n = {base_fr}){eu} ayant répondu à la question « {question} » · {filtres_txt}. "
        "Non représentatif de l'ensemble des développeurs."
    )


# --- Garde-fou : pas de figure sous l'effectif minimal ---
base_min = int(utilite.loc[utilite["Zone"] == "France", "base"].min())
if base_min < accueil.MIN_REPONDANTS:
    st.warning(
        f"Avec ces filtres, seulement {base_min} répondants en France ont répondu à la "
        f"question sur l'utilité de l'IA : sous le minimum de {accueil.MIN_REPONDANTS}, "
        "la marge d'erreur dépasserait ±10 points. Élargissez les filtres."
    )
    st.stop()

constat, explorer, donnees_tab = st.tabs(["Le constat", "Explorer", "Données"])

# =====================================================================================
# Onglet 1 · Le constat
# =====================================================================================
with constat:
    for col, k in zip(st.columns(4), axe_4.indicateurs(selection, exclure_na)):
        ecart = None if k["france"] is None or k["europe"] is None \
            else f"{100 * (k['france'] - k['europe']):+.1f} pts vs Europe".replace(".", ",")
        col.metric(k["libelle"], common.fmt(k["france"], "{:.0%}"), delta=ecart,
                   delta_color="off",
                   help=f"Europe : {common.fmt(k['europe'], '{:.0%}')} · base France "
                        f"n = {k['base']}")

    # Figure-clé (matplotlib, comme le recommande le cours) : France en couleur, Europe en gris.
    titre = ("L'IA est jugée utile pour coder, déboguer et documenter, "
             "pas pour concevoir ni communiquer"
             if vue_par_defaut else "Part des répondants jugeant l'IA utile, par tâche")
    large = utilite.pivot(index="tache", columns="Zone", values="part") \
        .reindex(list(axe_4.TACHES.values())).sort_values("France")
    fig, ax = plt.subplots(figsize=(9, 5.2))
    y = range(len(large))
    h = 0.38
    barres_fr = ax.barh([i + h / 2 for i in y], large["France"], height=h,
                        color=FRANCE_COULEUR, label="France")
    barres_eu = ax.barh([i - h / 2 for i in y], large["Europe"], height=h,
                        color=EUROPE_COULEUR, label="Europe")
    ax.bar_label(barres_fr, labels=[f"{v:.0%}" for v in large["France"]], padding=3,
                 fontsize=9, color=FRANCE_COULEUR, fontweight="bold")
    ax.bar_label(barres_eu, labels=[f"{v:.0%}" for v in large["Europe"]], padding=3,
                 fontsize=8, color=EUROPE_COULEUR)
    ax.set_yticks(list(y), large.index)
    ax.xaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax.set_xlim(0, 1)
    ax.set_xlabel("Part des répondants jugeant l'IA utile ou très utile", color="#666666")
    ax.set_title(textwrap.fill(titre, 70), loc="left", fontsize=12, fontweight="bold",
                 pad=24)
    ax.legend(frameon=False, loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, fontsize=9)
    for cote in ("top", "right", "left"):
        ax.spines[cote].set_visible(False)
    ax.tick_params(length=0)
    ax.grid(axis="x", color="#eeeeee")
    ax.set_axisbelow(True)
    fig.tight_layout()
    common.show_figure(fig)

    st.markdown(
        f"**👥 Population étudiée : {common.fmt(n_fr + n_eu, '{:,}')} répondants** "
        f"· France : **{common.fmt(n_fr, '{:,}')}** · Europe : **{common.fmt(n_eu, '{:,}')}** "
        f"· {filtres_txt}"
    )
    b = utilite.groupby("Zone")["base"].min()
    legende("Utilité de l'IA par tâche" + (" (hors « Non applicable »)" if exclure_na else ""),
            int(b["France"]), int(b["Europe"]))

# =====================================================================================
# Onglet 2 · Explorer : la nuance, le coût, l'organisation (graphiques natifs)
# =====================================================================================
with explorer:
    vue = st.radio(
        "Vue", ["Satisfaction par tâche", "Erreurs coûteuses", "Politique selon la taille"],
        horizontal=True, key="axe4_vue")

    if vue == "Satisfaction par tâche":
        sat = axe_4.satisfaction_par_tache(selection, "France")
        st.subheader("L'IA a-t-elle amélioré ou dégradé la satisfaction, tâche par tâche ?")
        trace = sat.melt(id_vars=["tache", "base"], value_vars=["ameliore", "degrade"],
                         var_name="Effet", value_name="part")
        trace["Effet"] = trace["Effet"].map({"ameliore": "Améliorée", "degrade": "Dégradée"})
        st.bar_chart(trace, x="tache", y="part", color="Effet", horizontal=True,
                     stack=False, x_label="Part des répondants", y_label="")
        legende("Effet de l'IA sur la satisfaction (France)", int(sat["base"].min()))

    elif vue == "Erreurs coûteuses":
        err = axe_4.erreurs_couteuses(selection)
        st.subheader("Les erreurs de l'IA qui ont fait perdre le plus de temps")
        # Une colonne par zone, dans l'ordre des couleurs : France en bleu, Europe en orange.
        large_err = err.pivot(index="erreur", columns="Zone", values="part")[["France", "Europe"]]
        st.bar_chart(large_err, color=[FRANCE_COULEUR, EUROPE_COULEUR], horizontal=True,
                     stack=False, x_label="Part des répondants", y_label="")
        bases = err.groupby("Zone")["base"].first()
        legende("Erreurs de l'IA les plus coûteuses (plusieurs réponses possibles)",
                int(bases["France"]), int(bases["Europe"]))

    else:
        pol = axe_4.politique_par_taille(selection, "France")
        st.subheader("Comment les entreprises encadrent l'IA, selon leur taille (France)")
        petits = pol.groupby("taille")["base"].first()
        affiche = pol[pol["base"] >= accueil.MIN_REPONDANTS]
        if affiche.empty:
            st.warning(f"Moins de {accueil.MIN_REPONDANTS} répondants dans chaque groupe "
                       "de taille avec ces filtres.")
        else:
            st.bar_chart(affiche, x="politique", y="part", color="taille", horizontal=True,
                         stack=False, x_label="Part des répondants", y_label="")
        masques = petits[petits < accueil.MIN_REPONDANTS]
        if not masques.empty:
            st.info("Masqué car sous le seuil : "
                    + ", ".join(f"{t} (n = {n})" for t, n in masques.items()))
        legende("Politique d'usage de l'IA dans l'organisation, par taille (France) ; "
                f"bases : {', '.join(f'{t} n = {n}' for t, n in petits.items())}",
                int(petits.sum()))

# =====================================================================================
# Onglet 3 · Données : les tables derrière les figures
# =====================================================================================
with donnees_tab:
    pct = st.column_config.NumberColumn(format="percent")
    st.markdown("**Utilité par tâche** (table de la figure-clé)")
    st.dataframe(utilite, hide_index=True, column_config={"part": pct})
    st.markdown("**Satisfaction par tâche (France)**")
    st.dataframe(axe_4.satisfaction_par_tache(selection, "France"), hide_index=True,
                 column_config={"ameliore": pct, "degrade": pct})
    st.markdown("**Erreurs coûteuses**")
    st.dataframe(axe_4.erreurs_couteuses(selection), hide_index=True,
                 column_config={"part": pct})
    st.markdown("**Politique d'usage selon la taille (France)**")
    st.dataframe(axe_4.politique_par_taille(selection, "France"), hide_index=True,
                 column_config={"part": pct})
