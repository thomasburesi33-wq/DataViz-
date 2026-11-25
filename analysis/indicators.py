"""Indicateurs génériques réutilisés par le tableau de bord et les cinq axes.

Chaque fonction renvoie une table (DataFrame) ou un nombre, jamais une figure :
la table derrière chaque graphique est ainsi testable hors de l'interface.
"""
from __future__ import annotations

import pandas as pd

from analysis import config


def _median_or_none(values: pd.Series) -> float | None:
    """Médiane d'une série numérique, ou None si elle est vide."""
    values = values.dropna()
    return None if values.empty else float(values.median())


def share_single(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Répartition d'une question à choix unique.

    Renvoie une ligne par modalité, triée par effectif décroissant, avec les colonnes
    option, n (répondants ayant choisi la modalité), base (répondants ayant répondu
    à la question) et share (n / base).
    """
    answers = df[column].dropna()
    base = len(answers)
    if base == 0:
        return pd.DataFrame(columns=["option", "n", "base", "share"])
    counts = answers.value_counts()
    return pd.DataFrame({
        "option": counts.index.astype(str),
        "n": counts.to_numpy(),
        "base": base,
        "share": counts.to_numpy() / base,
    })


def share_multi(df: pd.DataFrame, column: str, sep: str = config.MULTI_SEP) -> pd.DataFrame:
    """Répartition d'une question à choix multiples (« Python;SQL;Rust »).

    La base est le nombre de répondants ayant répondu à la question ; une même personne
    peut compter dans plusieurs modalités, donc les parts ne somment pas à 100 %.
    Mêmes colonnes que `share_single`.
    """
    answers = df[column].dropna()
    base = len(answers)
    if base == 0:
        return pd.DataFrame(columns=["option", "n", "base", "share"])
    counts = answers.str.split(sep).explode().str.strip().value_counts()
    return pd.DataFrame({
        "option": counts.index.astype(str),
        "n": counts.to_numpy(),
        "base": base,
        "share": counts.to_numpy() / base,
    })


def median_by(df: pd.DataFrame, value: str, by: str,
              min_n: int = config.MIN_N) -> pd.DataFrame:
    """Médiane de `value` par modalité de `by`.

    Renvoie une ligne par modalité avec les colonnes group, n et median ; la médiane
    vaut NaN quand le groupe compte moins de `min_n` répondants (effectif insuffisant).
    """
    sub = df[[by, value]].dropna()
    if sub.empty:
        return pd.DataFrame(columns=["group", "n", "median"])
    grouped = sub.groupby(by, observed=True)[value].agg(["size", "median"]).reset_index()
    grouped.columns = ["group", "n", "median"]
    grouped.loc[grouped["n"] < min_n, "median"] = float("nan")
    return grouped.sort_values("n", ascending=False, ignore_index=True)


def headline_kpis(df: pd.DataFrame) -> dict[str, float | int | None]:
    """Indicateurs du bandeau du tableau de bord principal.

    Renvoie n_respondents, share_code_main (part de ceux qui codent comme activité
    principale, parmi ceux qui ont répondu), median_work_exp (années) et
    median_comp_usd (rémunération annuelle convertie en dollars). None si non calculable.
    """
    code = df["CodeMain"].dropna() if "CodeMain" in df.columns else pd.Series(dtype=str)
    share_code = None if code.empty else float(
        code.str.startswith("I create code as a primary part").mean())
    return {
        "n_respondents": len(df),
        "share_code_main": share_code,
        "median_work_exp": _median_or_none(df.get("WorkExp", pd.Series(dtype=float))),
        "median_comp_usd": _median_or_none(
            df.get("ConvertedCompYearly", pd.Series(dtype=float))),
    }
