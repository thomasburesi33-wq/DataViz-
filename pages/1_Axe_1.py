"""Axe 1 · Adoption : où en sont les développeurs ?

Présentation uniquement : tous les calculs sont dans analysis/axe_1.py.
La page suit les cinq temps de l'enquête vus en cours : cadrer, faire connaissance avec les
données, explorer, mettre à l'épreuve, communiquer (le brief en tête de page).
"""
import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Axe 1 · Adoption de l'IA", layout="wide")

from analysis import accueil  # noqa: E402  (set_page_config doit passer en premier)
from analysis import axe_1 as axe  # noqa: E402
from analysis.axe_1 import fr_n, fr_pct, fr_pts  # noqa: E402
from ui import common  # noqa: E402

FRANCE_COULEUR, EUROPE_COULEUR, TRAIT = "#257de0", "#a3a3a3", "#d9d9d9"
ZONES = alt.Scale(domain=["France", "Europe"], range=[FRANCE_COULEUR, EUROPE_COULEUR])


@st.cache_data(show_spinner="Préparation des indicateurs de l'axe…")
def donnees_axe() -> pd.DataFrame:
    """Enquête 2026 et colonnes de l'axe, calculées une seule fois pour tous les visiteurs."""
    return axe.preparer(common.load_year(2026))


# =====================================================================================
# 1 · Cadrer : la question de la DSI
# =====================================================================================
st.title("Axe 1 · Adoption : où en sont les développeurs ?")
st.markdown(
    "**Question de la DSI :** qui utilise l'IA au travail, quels types d'outils, à quelle "
    "fréquence, et qui se forme ? C'est l'état des lieux de départ de la politique d'usage : "
    "avant de choisir des outils (axe 3) ou des règles (axe 4), il faut savoir d'où partent "
    "les développeurs. Comme sur la page principale, les répondants vivant en **France** sont "
    "comparés à ceux de **pays européens voisins**."
)

survey = donnees_axe()

# --- Filtres (barre latérale) : les clés commencent par axe1_ ---
with st.sidebar:
    st.subheader("Filtres de l'axe 1")
    europe = st.multiselect(
        "Pays européens comparés à la France", accueil.EUROPE_DEFAUT,
        default=accueil.EUROPE_DEFAUT, format_func=lambda c: accueil.NOMS_FR.get(c, c),
        key="axe1_europe", help="Les 8 pays de comparaison de la page principale",
    )
    ages = st.multiselect(
        "Âge", [a for a in axe.AGES_FR if a in set(survey["Age"].dropna())],
        format_func=axe.AGES_FR.get, key="axe1_ages", help="Vide = tous les âges",
    )
    experiences = st.multiselect(
        "Expérience professionnelle", axe.EXPERIENCES, key="axe1_experiences",
        help="Années de travail déclarées (WorkExp). Vide = toutes",
    )
    postes = st.multiselect(
        "Poste", axe.POSTES, key="axe1_postes",
        help="Les 41 postes de l'enquête regroupés en 5 familles. Vide = tous",
    )
    situations = st.multiselect(
        "Situation professionnelle", list(axe.SITUATIONS_FR.values()), key="axe1_situations",
        help="Salariés, indépendants, étudiants… Vide = toutes",
    )
    st.caption(f"Seuil d'affichage : {axe.MIN_REPONDANTS} répondants par zone, comme sur la "
               "page principale (marge d'erreur de ±10 points au plus).")

if not europe:
    st.warning("Choisissez au moins un pays européen dans la barre latérale.")
    st.stop()

sel = axe.filtrer(survey, europe, ages, experiences, postes, situations)
vue_par_defaut = (list(europe) == accueil.EUROPE_DEFAUT
                  and not (ages or experiences or postes or situations))

n_fr = int((sel["Zone"] == "France").sum())
n_eu = int((sel["Zone"] == "Europe").sum())
filtres_txt = " · ".join(
    [", ".join(axe.AGES_FR[a] for a in ages) if ages else "tous âges"]
    + ([", ".join(experiences)] if experiences else [])
    + ([", ".join(postes)] if postes else [])
    + ([", ".join(situations)] if situations else [])
)


def population(indicateurs: list[str]) -> None:
    """Sous chaque figure : qui, quelle année, combien de répondants (bases de calcul)."""
    t = axe.tableau(sel, indicateurs)
    bases = {z: t.loc[t["Zone"] == z, "base"] for z in ("France", "Europe")}

    def plage(serie: pd.Series) -> str:
        lo, hi = int(serie.min()), int(serie.max())
        return f"n = {fr_n(lo)}" if lo == hi else f"n = {fr_n(lo)} à {fr_n(hi)}"

    qui = list(dict.fromkeys(t["base_texte"]))
    st.caption(
        f"Population : répondants volontaires à l'enquête Stack Overflow 2026 · France "
        f"({plage(bases['France'])}) et {len(europe)} pays européens "
        f"({plage(bases['Europe'])}) · {filtres_txt} · base : {' ; '.join(qui)}. "
        "Non représentatif de l'ensemble des développeurs."
    )


def haltere(indicateurs: list[str], titre: str) -> None:
    """Figure en haltères : France en couleur (le message), Europe en gris (le contexte).
    Un indicateur dont une zone est sous le seuil d'effectif n'est pas tracé."""
    t = axe.tableau(sel, indicateurs)
    trop_petits = set(t.loc[t["base"] < axe.MIN_REPONDANTS, "indicateur"])
    donnees = t[~t["indicateur"].isin(trop_petits)].dropna(subset=["part"])
    if donnees.empty:
        st.info("Effectifs insuffisants pour tracer cette figure avec ces filtres.")
        return
    donnees = donnees.assign(part_txt=donnees["part"].map(fr_pct),
                             marge_txt=donnees["marge"].map(lambda m: "± " + fr_pct(m, 1)))
    ordre = [axe.libelle(i) for i in indicateurs]
    y = alt.Y("indicateur:N", sort=ordre, title=None, axis=alt.Axis(labelLimit=330))
    x = alt.X("part:Q", title="Part des répondants concernés",
              axis=alt.Axis(format="%", tickCount=5), scale=alt.Scale(domain=[0, 1]))
    infobulle = [alt.Tooltip("indicateur:N", title="Indicateur"), alt.Tooltip("Zone:N"),
                 alt.Tooltip("part_txt:N", title="Part"),
                 alt.Tooltip("marge_txt:N", title="Marge d'erreur (95 %)"),
                 alt.Tooltip("n:Q", title="Répondants concernés", format=",d"),
                 alt.Tooltip("base:Q", title="Base", format=",d"),
                 alt.Tooltip("base_texte:N", title="Qui a répondu")]
    base = alt.Chart(donnees)
    trait = base.mark_line(color=TRAIT, strokeWidth=3).encode(x=x, y=y, detail="indicateur:N")
    points = base.mark_circle(size=200, opacity=1).encode(
        x=x, y=y, tooltip=infobulle,
        color=alt.Color("Zone:N", scale=ZONES, legend=alt.Legend(title=None, orient="top")))
    valeurs = [base.transform_filter(alt.datum.Zone == zone).mark_text(
        dy=dy, fontSize=11, fontWeight="bold").encode(
        x=x, y=y, text="part_txt:N", color=alt.Color("Zone:N", scale=ZONES, legend=None))
        for zone, dy in (("France", -15), ("Europe", 15))]
    st.altair_chart((trait + points + valeurs[0] + valeurs[1]).properties(
        title=titre, height=62 * donnees["indicateur"].nunique() + 30), width="stretch")
    if trop_petits:
        st.info("Non tracé, moins de " + str(axe.MIN_REPONDANTS) + " répondants dans une zone : "
                + ", ".join(sorted(trop_petits)))
    population(indicateurs)


# --- Garde-fou : sans effectif suffisant, aucune figure ---
base_fr = axe.part(sel[sel["Zone"] == "France"], "utilise_ia")[2]
base_eu = axe.part(sel[sel["Zone"] == "Europe"], "utilise_ia")[2]
if min(base_fr, base_eu) < axe.MIN_REPONDANTS:
    st.warning(
        f"Avec ces filtres, la question sur l'usage de l'IA au travail ne compte que "
        f"{fr_n(min(base_fr, base_eu))} répondants dans une des deux zones (minimum : "
        f"{axe.MIN_REPONDANTS}). La marge d'erreur dépasserait ±10 points : élargissez les "
        "filtres dans la barre latérale."
    )
    st.stop()

adoption = axe.ecart(sel, "utilise_ia")
quotidien = axe.ecart(sel, "quotidien")
formation = axe.ecart(sel, "forme_travail")

constat_tab, explorer_tab, epreuve_tab, methode_tab = st.tabs(
    ["Le constat", "Explorer", "Mise à l'épreuve", "Données et méthode"])

# =====================================================================================
# 5 · Communiquer : le brief, la conclusion d'abord
# =====================================================================================
with constat_tab:
    with st.container(border=True):
        if vue_par_defaut:
            st.markdown(
                "#### En une phrase\n"
                "**En France, moins de développeurs ont adopté l'IA au travail que chez nos "
                "voisins européens, mais ceux qui l'ont adoptée s'en servent autant : le retard "
                "se joue à l'entrée, et il va de pair avec une formation au travail plus rare.**"
            )
        else:
            st.markdown("#### Votre sélection en une phrase")
        st.markdown(
            f"En France, **{fr_pct(adoption['france'])}** des répondants utilisent l'IA au "
            f"travail, contre **{fr_pct(adoption['europe'])}** en Europe "
            f"({fr_pts(adoption['ecart'])}). Parmi les utilisateurs, "
            f"**{fr_pct(quotidien['france'])}** s'en servent chaque jour, contre "
            f"**{fr_pct(quotidien['europe'])}** ({fr_pts(quotidien['ecart'])})."
        )

    k1, k2, k3, k4 = st.columns(4)
    for col, code, titre, aide in (
        (k1, "utilise_ia", "Utilisent l'IA au travail",
         "Parmi les répondants à la question sur l'usage de l'IA au travail"),
        (k2, "outil_1", "Utilisent un assistant de code",
         "Type d'outil le plus utilisé, parmi les mêmes répondants"),
        (k3, "quotidien", "Utilisateurs quotidiens",
         "Utilisent au moins un outil chaque jour, parmi les utilisateurs d'IA au travail"),
        (k4, "forme_travail", "Formés à l'IA au travail",
         "Parmi les répondants à la question sur la formation à l'IA"),
    ):
        e = axe.ecart(sel, code)
        # Signe moins ASCII : Streamlit en déduit le sens de la flèche.
        col.metric(titre, fr_pct(e["france"]),
                   delta=f"{fr_pts(e['ecart']).replace(chr(0x2212), '-')} vs Europe",
                   delta_color="off",
                   help=f"{aide}. Europe : {fr_pct(e['europe'])} · France n = "
                        f"{fr_n(e['base_france'])}, Europe n = {fr_n(e['base_europe'])}")

    # --- Figure-affirmation 1 : l'adoption ---
    st.subheader("1 · Qui utilise l'IA, et quels outils ?")
    haltere(["utilise_ia", "outil_1", "outil_2", "outil_3", "outil_4"],
            "Les Français adoptent moins l'IA au travail, pour chaque type d'outil"
            if vue_par_defaut else "Usage de l'IA au travail, par type d'outil")
    outils = [axe.ecart(sel, f"outil_{k}") for k in range(1, 5)]
    st.markdown(
        f"**Et alors ?** L'écart d'adoption ({fr_pts(adoption['ecart'])}, à ± "
        f"{fr_pts(adoption['marge']).lstrip('+')} près) "
        + ("dépasse la marge d'erreur" if adoption["significatif"]
           else "reste dans la marge d'erreur")
        + f". La France est en dessous sur {sum(o['ecart'] < 0 for o in outils)} types "
        f"d'outils sur 4, dont les agents et workflows automatisés, les plus avancés "
        f"({fr_pct(outils[2]['france'])} contre {fr_pct(outils[2]['europe'])}). Pour la DSI, "
        "la marge de progression est d'abord dans le nombre d'utilisateurs."
    )

    # --- Figure-affirmation 2 : l'intensité ---
    st.subheader("2 · À quelle fréquence ?")
    haltere(["quotidien", "quotidien_1", "quotidien_2", "plus_2h"],
            "Une fois adoptée, l'IA est utilisée aussi souvent en France qu'en Europe"
            if vue_par_defaut else "Fréquence d'usage chez les utilisateurs")
    plus_2h = axe.ecart(sel, "plus_2h")
    st.markdown(
        "**Et alors ?** Chez ceux qui utilisent l'IA, l'usage quotidien est "
        + ("comparable" if not quotidien["significatif"] else "différent")
        + f" ({fr_pts(quotidien['ecart'])}, à ± {fr_pts(quotidien['marge']).lstrip('+')} "
        f"près), tout comme le temps passé : {fr_pct(plus_2h['france'])} des utilisateurs "
        f"quotidiens y consacrent plus de 2 h par jour, contre {fr_pct(plus_2h['europe'])}. "
        "Les utilisateurs français ne sont pas moins convaincus : il ne s'agit pas d'intensifier "
        "l'usage, mais d'embarquer les non-utilisateurs."
    )

    # --- Figure-affirmation 3 : la formation ---
    st.subheader("3 · Qui se forme, et comment ?")
    haltere(["forme", "forme_travail", "moyen_1", "moyen_3", "moyen_2"],
            "Les Français se forment moins à l'IA, surtout au travail"
            if vue_par_defaut else "Formation à l'IA l'an dernier")
    forme = axe.ecart(sel, "forme")
    collegues, outils_ia = axe.ecart(sel, "moyen_1"), axe.ecart(sel, "moyen_3")
    st.markdown(
        f"**Et alors ?** {fr_pct(forme['france'])} des répondants français se sont formés à "
        f"l'IA l'an dernier, contre {fr_pct(forme['europe'])} ; au travail, "
        f"{fr_pct(formation['france'])} contre {fr_pct(formation['europe'])} "
        f"({fr_pts(formation['ecart'])}). Ceux qui se forment apprennent plus souvent auprès de "
        f"leurs collègues ({fr_pct(collegues['france'])} contre {fr_pct(collegues['europe'])}) "
        f"et moins par les outils d'IA eux-mêmes ({fr_pct(outils_ia['france'])} contre "
        f"{fr_pct(outils_ia['europe'])}) : en France, la formation passe davantage par l'équipe."
    )

    # --- Le brief : ce que nous savons, ne savons pas, recommandons ---
    st.subheader("Le brief pour la DSI")
    if not vue_par_defaut:
        st.caption("Le brief est rédigé et vérifié sur la population par défaut (8 pays, tous "
                   "profils) ; les chiffres des figures ci-dessus sont ceux de votre sélection.")
    savons, savons_pas, recommandons = st.columns(3)
    with savons.container(border=True):
        st.markdown(
            "**Ce que nous savons**\n\n"
            "- *Motif* : les répondants français utilisent moins l'IA au travail (75 % contre "
            "82 %) : sous chacun des 8 pays voisins, à chaque niveau d'expérience et à "
            "composition égale (voir « Mise à l'épreuve »).\n"
            "- *Constat* : l'écart touche les 4 types d'outils, dont les agents (17 % contre "
            "24 %).\n"
            "- *Constat* : chez les utilisateurs, l'usage quotidien est le même (72 %).\n"
            "- *Constat* : moins de formation à l'IA au travail (52 % contre 59 %)."
        )
    with savons_pas.container(border=True):
        st.markdown(
            "**Ce que nous ne savons pas**\n\n"
            "- *Pourquoi* l'écart existe : l'enquête ne demande pas si l'employeur fournit, "
            "autorise ou interdit l'IA. Les freins déclarés sont l'objet de l'axe 2.\n"
            "- Si les répondants ressemblent aux développeurs du groupe : ce sont des "
            "volontaires de Stack Overflow, pas un échantillon représentatif.\n"
            "- L'évolution : une seule année (2026) est analysée ici."
        )
    with recommandons.container(border=True):
        st.markdown(
            "**Ce que nous recommandons**\n\n"
            "- *Hypothèse* : le levier est l'accès et la formation au travail, pas "
            "l'intensité d'usage.\n"
            "- *Recommandation* : cibler les non-utilisateurs avec un outil d'entrée "
            "(l'assistant de code, le plus adopté) et une formation sur le poste, entre pairs.\n"
            "- *Vérification* : reposer la même question (usage de l'IA au travail) en interne "
            "à 6 et 12 mois ; l'objectif est de rejoindre le niveau européen (82 %)."
        )

# =====================================================================================
# 3 · Explorer : un indicateur, par pays ou par segment
# =====================================================================================
with explorer_tab:
    st.markdown("Choisissez un indicateur et une façon de découper les répondants. Les groupes "
                f"de moins de {axe.MIN_REPONDANTS} répondants ne sont pas tracés.")
    gauche, droite = st.columns([2, 1])
    themes = list(dict.fromkeys(t for t, _, _ in axe.INDICATEURS.values()))
    with droite:
        theme = st.radio("Thème", themes, key="axe1_theme", horizontal=True)
        comparer = st.radio("Comparer", ["Pays par pays", *axe.SEGMENTS], key="axe1_comparer")
    with gauche:
        choix = st.selectbox(
            "Indicateur", [c for c, (t, _, _) in axe.INDICATEURS.items() if t == theme],
            format_func=axe.libelle, key=f"axe1_indicateur_{theme}")

    if comparer == "Pays par pays":
        detail = axe.par_pays(sel, choix)
        affiches = detail[detail["base"] >= axe.MIN_REPONDANTS].dropna(subset=["part"])
        affiches = affiches.assign(part_txt=affiches["part"].map(fr_pct))
        moyenne = axe.part(sel[sel["Zone"] == "Europe"], choix)[0]
        barres = alt.Chart(affiches).mark_bar(cornerRadiusEnd=4, height=18).encode(
            x=alt.X("part:Q", title="Part des répondants concernés",
                    axis=alt.Axis(format="%"), scale=alt.Scale(domain=[0, 1])),
            y=alt.Y("pays:N", sort="-x", title=None),
            color=alt.condition(alt.datum.france, alt.value(FRANCE_COULEUR),
                                alt.value(EUROPE_COULEUR)),
            tooltip=[alt.Tooltip("pays:N", title="Pays"),
                     alt.Tooltip("part_txt:N", title="Part"),
                     alt.Tooltip("base:Q", title="Base", format=",d")])
        etiquettes = barres.mark_text(align="left", dx=4, fontSize=11).encode(
            text="part_txt:N", color=alt.value("#191919"))
        couches = barres + etiquettes
        if moyenne is not None:
            couches += alt.Chart(pd.DataFrame({"m": [moyenne]})).mark_rule(
                strokeDash=[4, 3], color="#666666").encode(x="m:Q")
        st.altair_chart(couches.properties(
            title=f"{axe.libelle(choix)}, pays par pays (pointillés : ensemble des pays "
                  "européens retenus)", height=34 * max(len(affiches), 3)), width="stretch")
        masques = detail[detail["base"] < axe.MIN_REPONDANTS]
        if not masques.empty:
            st.info("Masqués, moins de " + str(axe.MIN_REPONDANTS) + " répondants : " + ", ".join(
                f"{r.pays} (n = {r.base})" for r in masques.itertuples()))
        st.caption(
            "Population : répondants volontaires à l'enquête Stack Overflow 2026 · "
            f"{axe.INDICATEURS[choix][2]} · France et {len(europe)} pays européens · "
            f"{filtres_txt} · par pays : "
            + ", ".join(f"{r.pays} n = {fr_n(r.base)}" for r in affiches.itertuples())
            + ". Non représentatif de l'ensemble des développeurs.")
    else:
        colonne = axe.SEGMENTS[comparer]
        detail = axe.par_segment(sel, choix, colonne)
        traces = detail[detail["affiche"]].dropna(subset=["part"])
        if traces.empty:
            st.info("Aucun groupe n'atteint le seuil d'effectif avec ces filtres.")
        else:
            traces = traces.assign(part_txt=traces["part"].map(fr_pct))
            ordre = list(dict.fromkeys(traces["segment"]))
            barres = alt.Chart(traces).mark_bar(cornerRadiusEnd=4).encode(
                y=alt.Y("segment:N", sort=ordre, title=None),
                yOffset=alt.YOffset("Zone:N", sort=["France", "Europe"]),
                x=alt.X("part:Q", title="Part des répondants concernés",
                        axis=alt.Axis(format="%"), scale=alt.Scale(domain=[0, 1])),
                color=alt.Color("Zone:N", scale=ZONES,
                                legend=alt.Legend(title=None, orient="top")),
                tooltip=[alt.Tooltip("segment:N", title=comparer), alt.Tooltip("Zone:N"),
                         alt.Tooltip("part_txt:N", title="Part"),
                         alt.Tooltip("base:Q", title="Base", format=",d")])
            etiquettes = barres.mark_text(align="left", dx=4, fontSize=10).encode(
                text="part_txt:N", color=alt.value("#191919"))
            st.altair_chart((barres + etiquettes).properties(
                title=f"{axe.libelle(choix)}, selon {comparer.lower()}",
                height=alt.Step(24)), width="stretch")
        masques = detail[~detail["affiche"]]
        if not masques.empty:
            st.info("Non tracés, moins de " + str(axe.MIN_REPONDANTS) + " répondants : "
                    + ", ".join(f"{r.segment} · {r.Zone} (n = {r.base})"
                                for r in masques.itertuples()))
        bases = detail.groupby("Zone")["base"].sum()
        st.caption(
            "Population : répondants volontaires à l'enquête Stack Overflow 2026 · "
            f"{axe.INDICATEURS[choix][2]} ayant renseigné « {comparer.lower()} » · "
            f"France et {len(europe)} pays européens · {filtres_txt} · France n = {fr_n(int(bases.get('France', 0)))}, "
            f"Europe n = {fr_n(int(bases.get('Europe', 0)))}. "
            "Non représentatif de l'ensemble des développeurs.")

    # --- Répartition complète d'une question à choix unique ---
    st.divider()
    st.subheader("Répartition complète des réponses")
    questions = {
        "Temps passé chaque jour avec l'IA": ("AIDaily", axe.TEMPS_QUOTIDIEN_FR,
                                              "utilisateurs quotidiens d'IA"),
        "Formation à l'IA l'an dernier": ("LearnAI", axe.FORMATION_FR,
                                          "répondants à la question sur la formation"),
        **{f"Fréquence d'usage : {lib[0].lower() + lib[1:]}":
           (freq, axe.FREQUENCES_FR, f"utilisateurs de ce type d'outil")
           for _, lib, freq in axe.OUTILS},
    }
    question = st.selectbox("Question", list(questions), key="axe1_repartition")
    colonne, libelles, qui = questions[question]
    rep = axe.repartition(sel, colonne, libelles).dropna(subset=["part"])
    if rep.empty or rep.groupby("Zone")["base"].first().min() < axe.MIN_REPONDANTS:
        st.info(f"Moins de {axe.MIN_REPONDANTS} répondants dans une zone pour cette question "
                "avec ces filtres.")
    else:
        rep = rep.assign(part_txt=rep["part"].map(fr_pct))
        teintes = ["#cfe3fa", "#9cc5f3", "#5fa3ea", "#257de0", "#1559a8"][:len(libelles)]
        # Légende écrite à la main : la légende Altair écrase les barres empilées dans
        # Streamlit. Les couleurs vont du clair (moins) au foncé (plus).
        st.markdown("**" + question + "**  \n" + " &nbsp; ".join(
            f"<span style='color:{c}'>■</span> {lib}"
            for c, lib in zip(teintes, libelles.values())), unsafe_allow_html=True)
        st.altair_chart(alt.Chart(rep).mark_bar().encode(
            y=alt.Y("Zone:N", sort=["France", "Europe"], title=None,
                    scale=alt.Scale(paddingInner=0.3)),
            x=alt.X("part:Q", stack="normalize", title="Part des répondants",
                    axis=alt.Axis(format="%")),
            color=alt.Color("reponse:N", legend=None,
                            scale=alt.Scale(domain=list(libelles.values()), range=teintes)),
            order=alt.Order("ordre:Q"),
            tooltip=[alt.Tooltip("Zone:N"), alt.Tooltip("reponse:N", title="Réponse"),
                     alt.Tooltip("part_txt:N", title="Part"),
                     alt.Tooltip("n:Q", title="Répondants", format=",d"),
                     alt.Tooltip("base:Q", title="Base", format=",d")],
        ).properties(height=alt.Step(48)), width="stretch")
        bases = rep.groupby("Zone")["base"].first()
        st.caption(
            f"Population : répondants volontaires à l'enquête Stack Overflow 2026 · {qui} · "
            f"France et {len(europe)} pays européens · {filtres_txt} · France n = {fr_n(int(bases['France']))}, Europe "
            f"n = {fr_n(int(bases['Europe']))}. Non représentatif de l'ensemble des "
            "développeurs.")

# =====================================================================================
# 4 · Mettre à l'épreuve : l'affirmation centrale résiste-t-elle ?
# =====================================================================================
with epreuve_tab:
    st.markdown(
        "**L'affirmation éprouvée :** *« en France, moins de répondants utilisent l'IA au "
        "travail qu'en Europe »*. Chaque test ci-dessous pourrait la faire tomber : une "
        "affirmation n'est défendue que si elle y résiste. Les tests sont recalculés selon les "
        "filtres de la barre latérale."
    )
    preuves = axe.table_de_preuves(sel)
    verdicts = {True: "✅ Tient", False: "❌ Ne tient pas"}
    st.table(
        preuves.assign(tient=preuves["tient"].map(lambda v: verdicts.get(v, "— Non calculable")))
        .rename(columns={"test": "Test", "resultat": "Résultat", "tient": "Verdict"})
        .set_index("Test"))

    st.subheader("Le paradoxe de Simpson : l'écart tient-il dans chaque groupe ?")
    st.markdown("Un écart global peut disparaître, voire s'inverser, à l'intérieur des groupes "
                "si la France et l'Europe n'ont pas les mêmes profils de répondants. On le "
                "vérifie groupe par groupe.")
    segment = st.radio("Découper selon", list(axe.SEGMENTS), key="axe1_segment_epreuve",
                       horizontal=True, index=1)
    ecarts = axe.ecarts_par_segment(sel, "utilise_ia", axe.SEGMENTS[segment])
    if ecarts.empty:
        st.info(f"Aucun groupe ne compte {axe.MIN_REPONDANTS} répondants dans chaque zone.")
    else:
        ecarts = ecarts.assign(bas=ecarts["ecart"] - ecarts["marge"],
                               haut=ecarts["ecart"] + ecarts["marge"],
                               ecart_txt=ecarts["ecart"].map(fr_pts),
                               france_txt=ecarts["france"].map(fr_pct),
                               europe_txt=ecarts["europe"].map(fr_pct))
        y = alt.Y("segment:N", sort=list(ecarts["segment"]), title=None)
        x = alt.X("ecart:Q", title="Écart France − Europe (points), avec sa marge d'erreur",
                  axis=alt.Axis(tickCount=8))
        moustaches = alt.Chart(ecarts).mark_rule(color="#9cc5f3", strokeWidth=3).encode(
            y=y, x="bas:Q", x2="haut:Q")
        points = alt.Chart(ecarts).mark_circle(size=160, color=FRANCE_COULEUR,
                                               opacity=1).encode(
            y=y, x=x, tooltip=[alt.Tooltip("segment:N", title=segment),
                               alt.Tooltip("ecart_txt:N", title="Écart"),
                               alt.Tooltip("france_txt:N", title="France"),
                               alt.Tooltip("europe_txt:N", title="Europe"),
                               alt.Tooltip("base_france:Q", title="France n"),
                               alt.Tooltip("base_europe:Q", title="Europe n")])
        zero = alt.Chart(pd.DataFrame({"z": [0]})).mark_rule(color="#666666").encode(x="z:Q")
        st.altair_chart((zero + moustaches + points).properties(
            title=f"Utilisent l'IA au travail : écart France − Europe selon {segment.lower()}",
            height=max(60 * len(ecarts), 120)), width="stretch")
        st.caption(
            "Lecture : un point à gauche de la ligne verticale signifie moins d'utilisateurs en "
            "France ; si le trait ne coupe pas la ligne, l'écart dépasse la marge d'erreur. "
            "Chaque groupe est plus petit que l'ensemble, donc sa marge est plus large : "
            "c'est la régularité du signe d'un groupe à l'autre qui compte. "
            "Population : répondants volontaires à l'enquête Stack Overflow 2026 ayant répondu "
            f"sur l'usage de l'IA au travail · France et {len(europe)} pays européens · "
            f"{filtres_txt} · groupes d'au moins "
            f"{axe.MIN_REPONDANTS} répondants par zone : "
            + ", ".join(f"{r.segment} (France n = {fr_n(r.base_france)}, Europe "
                        f"n = {fr_n(r.base_europe)})" for r in ecarts.itertuples()) + ".")

    st.subheader("L'échelle des affirmations")
    st.markdown("Toutes les phrases du brief n'ont pas le même statut. Des données d'enquête "
                "établissent des constats et des motifs ; elles ne démontrent pas une cause.")
    st.table(pd.DataFrame([
        ("Moins de répondants utilisent l'IA au travail en France qu'en Europe", "Motif",
         "Tient dans tous les tests ci-dessus : marge d'erreur, 8 pays, segments, composition"),
        ("L'écart touche chaque type d'outil, dont les agents", "Constat",
         "Calculé sur 648 répondants en France ; écarts au-delà de la marge d'erreur"),
        ("Les utilisateurs français s'en servent aussi souvent", "Constat",
         "Écart de l'usage quotidien dans la marge d'erreur (488 utilisateurs en France)"),
        ("Les Français se forment moins à l'IA au travail", "Constat",
         "Écart de −7 points, au-delà de la marge d'erreur (794 répondants en France)"),
        ("Le retard vient de l'accès et de la formation en entreprise", "Hypothèse",
         "Plausible (écart concentré chez les salariés, quasi nul chez les étudiants), non démontré : "
         "l'enquête ne dit pas ce que l'employeur fournit ou autorise"),
        ("Cibler les non-utilisateurs : outil d'entrée et formation entre pairs",
         "Recommandation", "À vérifier en interne, avec la même question à 6 et 12 mois"),
    ], columns=["Affirmation", "Niveau", "Sur quoi elle repose"]).set_index("Affirmation"))
    st.caption("Échelle rédigée et vérifiée sur la population par défaut (8 pays, tous profils).")

# =====================================================================================
# 2 · Faire connaissance avec les données
# =====================================================================================
with methode_tab:
    st.subheader("La biographie des données")
    st.markdown(
        "- **Producteur et finalité** : Stack Overflow, enquête annuelle auprès des "
        "développeurs, publiée en accès libre ([restitution officielle]"
        "(https://survey.stackoverflow.co/2026)).\n"
        "- **Collecte** : questionnaire en ligne, rempli par des **volontaires**. Les "
        "répondants sont plus engagés que la moyenne des développeurs : les parts décrivent "
        "ces répondants, pas l'ensemble de la profession.\n"
        "- **Unité d'observation** : une ligne = un répondant.\n"
        "- **Population de l'axe** : répondants vivant en France ou dans les pays européens "
        "de comparaison, filtrés selon la barre latérale.\n"
        "- **Qui manque** : les développeurs qui ne fréquentent pas Stack Overflow, et ceux "
        "qui ont arrêté le questionnaire avant les questions sur l'IA."
    )

    st.subheader("Les questions de l'axe, et à qui elles sont posées")
    st.markdown("Le questionnaire est filtré : certaines questions ne sont posées qu'à une "
                "partie des répondants. Chaque part est donc calculée sur **sa propre base**.")
    st.table(pd.DataFrame([
        ("AISelect", "Do you currently use AI tools or AI agents in your role at work?",
         "Choix multiples", "Répondants arrivés à la section IA"),
        ("AIFreq_1 à 4", "How often do you use each of these AI tools or AI agents in your "
         "role at work?", "Une fréquence par outil", "Ceux qui ont coché l'outil dans AISelect"),
        ("AIDaily", "How much of your workday do you use AI tools to help you work?",
         "Choix unique", "Ceux qui utilisent au moins un outil chaque jour"),
        ("LearnAI", "In the last year, did you spend time learning AI programming or "
         "AI-enabled tooling on your own or at work?", "Choix unique", "Tous les répondants"),
        ("LearnAIHow", "How did you learn to code for AI in the past year?", "Choix multiples",
         "Ceux qui se sont formés (LearnAI = oui)"),
        ("Age, WorkExp, Role, Employment", "Âge, années d'expérience professionnelle, poste, "
         "situation professionnelle", "Segments", "Tous les répondants"),
    ], columns=["Colonne", "Question (texte original)", "Type", "Posée à"]).set_index("Colonne"))

    st.subheader("Qui répond à quoi, avec vos filtres")
    st.dataframe(axe.entonnoir(sel), hide_index=True, width="stretch",
                 column_config={"etape": "Étape du questionnaire",
                                "France": st.column_config.NumberColumn("France", format="%d"),
                                "Europe": st.column_config.NumberColumn("Europe", format="%d")})

    with st.expander("Journal d'exploration : je remarque, je me demande"):
        st.markdown(
            "Les observations de la phase d'exploration, sur la population par défaut. Chacune "
            "sépare ce que l'on voit de la question qu'elle fait naître ; les trois questions "
            "retenues sont devenues les trois figures du constat.\n\n"
            "1. **Je remarque** que 25 % des répondants français n'utilisent pas l'IA au "
            "travail, contre 18 % en Europe. **Je me demande** si cela tient à leur profil "
            "(plus jeunes, plus d'étudiants ?).\n"
            "2. **Je remarque** que la France est la dernière des 9 pays, au coude à coude avec "
            "le Royaume-Uni (76 %), loin de l'Espagne (89 %). **Je me demande** si l'écart vient "
            "d'un seul pays de comparaison.\n"
            "3. **Je remarque** que les 4 types d'outils sont moins cités en France, les "
            "chatbots (54 % contre 63 %) et les agents (17 % contre 24 %) surtout. **Je me "
            "demande** si les utilisateurs français sont aussi moins assidus.\n"
            "4. **Je remarque** que, parmi les utilisateurs, 72 % s'en servent chaque jour des "
            "deux côtés. **Je me demande** si le temps passé diffère.\n"
            "5. **Je remarque** que la part des plus de 2 h par jour est proche (49 % contre "
            "51 %). **Je me demande** si l'écart d'adoption se concentre dans un groupe.\n"
            "6. **Je remarque** que l'écart est de −9 points chez les salariés, mais quasi nul "
            "chez les étudiants (62 % des deux côtés). **Je me demande** si c'est "
            "l'entreprise qui fait la différence.\n"
            "7. **Je remarque** que 30 % des Français ne se sont pas formés à l'IA, contre "
            "25 %. **Je me demande** où se fait la différence : seul ou au travail ?\n"
            "8. **Je remarque** que les Français formés apprennent plus par leurs collègues "
            "(43 % contre 38 %) et moins par les outils d'IA (43 % contre 51 %). **Je me "
            "demande** si la formation entre pairs est un levier pour la DSI."
        )

    st.subheader("Toutes les valeurs de l'axe")
    complet = axe.tableau(sel, list(axe.INDICATEURS))
    st.dataframe(
        complet[["indicateur", "Zone", "part", "marge", "n", "base", "base_texte"]].assign(
            part=complet["part"] * 100, marge=complet["marge"] * 100),
        hide_index=True, width="stretch",
        column_config={
            "indicateur": "Indicateur",
            "part": st.column_config.NumberColumn("Part (%)", format="%.1f"),
            "marge": st.column_config.NumberColumn("Marge d'erreur (± points, 95 %)",
                                                   format="%.1f"),
            "n": st.column_config.NumberColumn("Concernés", format="%d"),
            "base": st.column_config.NumberColumn("Base", format="%d"),
            "base_texte": "Qui a répondu",
        },
    )
    st.download_button(
        "Télécharger la table (CSV)",
        complet.to_csv(index=False).encode("utf-8"),
        file_name="axe1_adoption_ia.csv", mime="text/csv", key="axe1_telecharger",
    )
    st.caption(
        f"Population : répondants volontaires à l'enquête Stack Overflow 2026 · France "
        f"(n = {fr_n(n_fr)}) et {len(europe)} pays européens (n = {fr_n(n_eu)}) · "
        f"{filtres_txt}. Marge d'erreur : intervalle de confiance à 95 % d'une part, "
        "1,96 × √(p(1 − p)/n). Non représentatif de l'ensemble des développeurs."
    )
