"""Axe 3 — Outils et modèles : quoi fournir ?

Responsable : à compléter (voir CADRAGE.md).
Question de la DSI : quels assistants de code et quels fournisseurs de modèles sont
utilisés ? Y a-t-il une option européenne (Mistral) ? Pourquoi les développeurs
changent-ils d'outil ?

Comparaison : la France face aux 8 pays européens retenus par le groupe
(Allemagne, Royaume-Uni, Pays-Bas, Espagne, Italie, Pologne, Suède, Suisse).

Toute la logique propre à cet axe vit ici, sans Streamlit ; la page pages/3_Axe_3.py
ne fait qu'afficher. Travaillez sur la branche axe-3.
"""
from __future__ import annotations

import pandas as pd

from analysis import accueil, indicators

# Questions de l'enquête mobilisées par l'axe.
QUESTION_AGENTS = "AICodeAgentHaveWorkedWith"   # assistants de code, choix multiples
QUESTION_LLMS = "LLMHaveWorkedWith"             # fournisseurs de modèles, choix multiples
QUESTION_SWITCH = "AIToolSwitch"                # changement d'outil, choix unique

# Filtre propre à l'axe (en plus de la comparaison France / Europe) : le poste.
AXIS_FILTER = "Role"

# Les options européennes que la DSI cherche à identifier (souveraineté, RSE).
EUROPEAN_AGENT = "Mistral Vibe"
EUROPEAN_LLM = "Mistral AI"

# Modalités de AIToolSwitch : « Yes — <raison> », « No », ou non concerné.
SWITCH_YES = "Yes — "
SWITCH_NA = "Not applicable — I do not use AI tools for work"

def filter_axis(df: pd.DataFrame, values: list[str]) -> pd.DataFrame:
    """Garde les répondants dont le poste (Role) est dans `values` ; liste vide = pas de filtre."""
    return df[df[AXIS_FILTER].isin(values)] if values else df

def filtrer_population(df: pd.DataFrame, europe: list[str] | None = None,
                       roles: list[str] | None = None) -> pd.DataFrame:
    """Garde la France et les pays européens de comparaison, ajoute la colonne Zone.

    `europe` vide ou None = les 8 pays retenus par défaut (accueil.EUROPE_DEFAUT) ;
    `roles` vide ou None = tous les postes. La colonne Zone vaut « France » ou
    « Europe » et sert à produire les figures en vis-à-vis.
    """
    selection = accueil.filtrer(df, europe or accueil.EUROPE_DEFAUT)
    return filter_axis(selection, roles or [])

def code_agents_table(df: pd.DataFrame) -> pd.DataFrame:
    """Part des répondants ayant utilisé chaque assistant de code dans l'année écoulée.

    Question à choix multiples : la base est le nombre de répondants ayant répondu
    à la question, et les parts ne somment pas à 100 %. La page appelle cette
    fonction deux fois : sur la zone France et sur la zone Europe.
    """
    return indicators.share_multi(df, QUESTION_AGENTS)

def llm_vendors_table(df: pd.DataFrame) -> pd.DataFrame:
    """Part des répondants ayant utilisé chaque fournisseur de modèles dans l'année écoulée.

    Même convention de base que `code_agents_table`.
    """
    return indicators.share_multi(df, QUESTION_LLMS)

def switch_table(df: pd.DataFrame) -> pd.DataFrame:
    """Raisons du changement d'outil IA, parmi les seuls répondants ayant changé.

    Les modalités « No » et « Not applicable » sont exclues : la base est le nombre
    de répondants ayant changé d'outil, et le motif « Yes — » est retiré des libellés.
    """
    reasons = (
        df[QUESTION_SWITCH].dropna()
        .loc[lambda s: s.str.startswith(SWITCH_YES)]
        .str.removeprefix(SWITCH_YES)
    )
    if reasons.empty:
        return pd.DataFrame(columns=["option", "n", "base", "share"])
    counts = reasons.value_counts()
    base = len(reasons)
    return pd.DataFrame({
        "option": counts.index.astype(str),
        "n": counts.to_numpy(),
        "base": base,
        "share": counts.to_numpy() / base,
    })

def kpis(df: pd.DataFrame) -> dict[str, object]:
    """Indicateurs d'une zone (France ou Europe), calculés sur la base de chaque question.

    Renvoie notamment top_agent / top_llm (modalité la plus citée et sa part),
    mistral_agent / mistral_llm ((n, share) ou None) et share_switched (part des
    utilisateurs d'outils IA ayant changé d'outil dans l'année ; les « Not applicable »,
    qui n'utilisent pas l'IA, sont exclus de la base). None quand non calculable.
    La page appelle cette fonction deux fois, par zone, et affiche l'écart en points.
    """
    agents = code_agents_table(df)
    llms = llm_vendors_table(df)
    switch_users = df[QUESTION_SWITCH].dropna()
    switch_users = switch_users[switch_users != SWITCH_NA]
    n_switched = int(switch_users.str.startswith(SWITCH_YES).sum())

    def _option(table: pd.DataFrame, option: str) -> tuple[int, float] | None:
        row = table.loc[table["option"] == option]
        return None if row.empty else (int(row["n"].iloc[0]), float(row["share"].iloc[0]))

    return {
        "n_population": len(df),
        "top_agent": agents["option"].iloc[0] if len(agents) else None,
        "top_agent_share": float(agents["share"].iloc[0]) if len(agents) else None,
        "top_llm": llms["option"].iloc[0] if len(llms) else None,
        "top_llm_share": float(llms["share"].iloc[0]) if len(llms) else None,
        "mistral_agent": _option(agents, EUROPEAN_AGENT),
        "mistral_llm": _option(llms, EUROPEAN_LLM),
        "n_switched": n_switched,
        "switch_base": len(switch_users),
        "share_switched": None if switch_users.empty else n_switched / len(switch_users),
    }