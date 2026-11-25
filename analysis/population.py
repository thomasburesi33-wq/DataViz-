"""Population : qui est dans une figure, quelle année, combien de répondants.

Chaque figure de l'application affiche la phrase produite par `population_caption`.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from analysis import config


def filter_population(df: pd.DataFrame, countries: list[str] | None = None,
                      code_main: list[str] | None = None,
                      employment: list[str] | None = None) -> pd.DataFrame:
    """Renvoie les répondants retenus par les filtres de population.

    Une liste vide ou None signifie « pas de filtre sur cette colonne ».
    """
    mask = pd.Series(True, index=df.index)
    for col, values in (("Country", countries), ("CodeMain", code_main),
                        ("Employment", employment)):
        if values and col in df.columns:
            mask &= df[col].isin(values)
    return df[mask]


def answered(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Renvoie les répondants qui ont répondu à la question `column`."""
    return df[df[column].notna()]


@dataclass(frozen=True)
class Population:
    """Description d'une population affichée sous une figure."""

    year: int
    who: str
    n: int

    @property
    def is_small(self) -> bool:
        """Vrai sous l'effectif minimal : la figure doit être signalée comme fragile."""
        return self.n < config.MIN_N


def describe_population(df: pd.DataFrame, year: int, countries: list[str] | None = None,
                        code_main: list[str] | None = None,
                        employment: list[str] | None = None,
                        extra: str | None = None) -> Population:
    """Renvoie la description de la population `df` à partir des filtres qui l'ont produite.

    `extra` précise un sous-ensemble propre à une figure, par exemple
    « ayant répondu à la question sur les langages ».
    """
    parts = [", ".join(countries) if countries else "tous pays"]
    if code_main:
        parts.append(" ou ".join(code_main))
    if employment:
        parts.append(" ou ".join(employment))
    if extra:
        parts.append(extra)
    return Population(year=year, who=" · ".join(parts), n=len(df))


def population_caption(pop: Population) -> str:
    """Renvoie la phrase de population à afficher sous une figure."""
    n = f"{pop.n:,}".replace(",", "\u202f")
    return (f"Population : répondants volontaires à l'enquête Stack Overflow {pop.year} "
            f"· {pop.who} · n = {n} répondants")
