"""Figures matplotlib de l'application, construites à partir des tables de `analysis`.

Ce module ne calcule rien et n'importe pas Streamlit : il reçoit une table, renvoie une figure.
La page l'affiche avec st.pyplot(fig) puis ferme la figure.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # aucun affichage graphique requis : fonctionne sur un serveur

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.ticker import PercentFormatter

# Palette de référence (skill dataviz) : une seule teinte pour une seule série.
SERIES_1 = "#257de0"
SERIES_2 = "#f47230"   # deuxième série, par exemple 2025 face à 2026
TEXT_PRIMARY = "#191919"
TEXT_SECONDARY = "#666666"
GRID = "#e7e7e7"
AXIS = "#c2c2c2"


def _style(ax: plt.Axes) -> None:
    """Axes discrets : grille fine, pas de cadre haut ni droit, textes en encre de texte."""
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(AXIS)
    ax.tick_params(colors=TEXT_SECONDARY, length=0)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def barh_shares(table: pd.DataFrame, title: str, top: int = 12,
                xlabel: str = "Part des répondants") -> Figure:
    """Barres horizontales des `top` premières modalités d'une table de parts
    (colonnes option et share, triées par part décroissante)."""
    data = table.head(top).iloc[::-1]   # la plus grande barre en haut
    fig, ax = plt.subplots(figsize=(8, 0.4 * max(len(data), 3) + 1.2))
    bars = ax.barh(data["option"], data["share"], color=SERIES_1, height=0.7)
    ax.bar_label(bars, labels=[f"{s:.0%}" for s in data["share"]], padding=4,
                 color=TEXT_PRIMARY, fontsize=9)
    ax.xaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax.set_xlim(0, max(float(data["share"].max()) * 1.15, 0.05) if len(data) else 1)
    ax.set_xlabel(xlabel, color=TEXT_SECONDARY)
    ax.set_title(title, loc="left", color=TEXT_PRIMARY, fontsize=12, fontweight="bold")
    _style(ax)
    fig.tight_layout()
    return fig


def barh_medians(table: pd.DataFrame, title: str, xlabel: str) -> Figure:
    """Barres horizontales des médianes par groupe (colonnes group, median) ;
    les groupes à effectif insuffisant (median NaN) sont absents de la figure."""
    data = table.dropna(subset=["median"]).sort_values("median")
    fig, ax = plt.subplots(figsize=(8, 0.4 * max(len(data), 3) + 1.2))
    bars = ax.barh(data["group"].astype(str), data["median"], color=SERIES_1, height=0.7)
    ax.bar_label(bars, labels=[f"{m:,.0f}".replace(",", "\u202f") for m in data["median"]],
                 padding=4, color=TEXT_PRIMARY, fontsize=9)
    ax.set_xlabel(xlabel, color=TEXT_SECONDARY)
    ax.set_title(title, loc="left", color=TEXT_PRIMARY, fontsize=12, fontweight="bold")
    _style(ax)
    fig.tight_layout()
    return fig
