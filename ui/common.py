"""Briques d'interface partagées par toutes les pages : cache, filtres de population,
données de session, affichage de la population et des indicateurs.

C'est le seul endroit, avec les pages, où l'on importe Streamlit.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from matplotlib.figure import Figure

from analysis import config, harmonisation, load, population


# --- Cache ------------------------------------------------------------------------------
# Le chargement (lecture d'un CSV de ~120 Mo) est la seule opération coûteuse : il est mis
# en cache une fois pour toutes les pages et tous les utilisateurs. Les filtres, rapides,
# ne le sont pas. Ne jamais muter les DataFrames renvoyés : .assign() / .copy().

@st.cache_data(show_spinner="Chargement des réponses à l'enquête…")
def load_year(year: int = config.MAIN_YEAR) -> pd.DataFrame:
    """Réponses de l'année, mises en cache."""
    return load.load_survey(year)


@st.cache_data(show_spinner="Chargement et harmonisation des réponses 2025…")
def load_2025_harmonised() -> pd.DataFrame:
    """Réponses 2025 harmonisées sur le référentiel 2026, mises en cache."""
    return harmonisation.harmonise_2025(load.load_survey(config.COMPARISON_YEAR))


@st.cache_data
def load_schema(year: int = config.MAIN_YEAR) -> pd.DataFrame:
    """Dictionnaire des questions de l'année, mis en cache."""
    return load.load_schema(year)


# --- Données de session -----------------------------------------------------------------
# Les filtres de population sont communs à toutes les pages. Streamlit efface l'état d'un
# widget quand on change de page : on garde donc la valeur sous une clé permanente
# (pop_*) et on la recopie dans la clé du widget (_w_pop_*) à chaque affichage.

def _restore(key: str, default: list[str]) -> None:
    if key not in st.session_state:
        st.session_state[key] = list(default)
    st.session_state[f"_w_{key}"] = st.session_state[key]


def _save(key: str) -> None:
    st.session_state[key] = st.session_state[f"_w_{key}"]


def _multiselect(label: str, key: str, options: list[str], default: list[str],
                 help_text: str) -> list[str]:
    _restore(key, [v for v in default if v in options])
    return st.multiselect(label, options, key=f"_w_{key}", on_change=_save, args=(key,),
                          help=help_text)


def population_filters(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, list[str]]]:
    """Affiche les filtres de population dans la barre latérale et renvoie
    (répondants retenus, filtres choisis). Les options viennent des données."""
    def options(col: str) -> list[str]:
        return sorted(df[col].dropna().unique().tolist()) if col in df.columns else []

    with st.sidebar:
        st.subheader("Population")
        filters = {
            "countries": _multiselect("Pays", "pop_countries", options("Country"),
                                      config.DEFAULT_COUNTRIES, "Vide = tous les pays"),
            "code_main": _multiselect("Rapport au code", "pop_code_main", options("CodeMain"),
                                      config.DEFAULT_CODE_MAIN, "Vide = tous les profils"),
            "employment": _multiselect("Situation professionnelle", "pop_employment",
                                       options("Employment"), config.DEFAULT_EMPLOYMENT,
                                       "Vide = toutes les situations"),
        }
    return population.filter_population(df, **filters), filters


# --- Affichage --------------------------------------------------------------------------

def show_population(df: pd.DataFrame, filters: dict[str, list[str]],
                    year: int = config.MAIN_YEAR, extra: str | None = None) -> None:
    """Affiche sous une figure qui, quelle année, combien de répondants,
    et avertit quand l'effectif est sous le seuil minimal."""
    pop = population.describe_population(df, year, extra=extra, **filters)
    st.caption(population.population_caption(pop))
    if pop.is_small:
        st.warning(f"Moins de {config.MIN_N} répondants : résultat indicatif, à ne pas "
                   "généraliser.")


def stop_if_empty(df: pd.DataFrame) -> None:
    """Arrête la page avec un message si la sélection est vide."""
    if df.empty:
        st.warning("Aucun répondant ne correspond à ces filtres : élargissez la population.")
        st.stop()


def show_figure(fig: Figure) -> None:
    """Affiche une figure matplotlib puis la ferme pour libérer la mémoire."""
    st.pyplot(fig)
    plt.close(fig)


def fmt(value: float | int | None, pattern: str = "{:.2f}") -> str:
    """Formate une valeur pour st.metric ; None devient « — »."""
    if value is None:
        return "—"
    return pattern.format(value).replace(",", "\u202f")


def volunteer_notice() -> None:
    """Rappel obligatoire : les répondants sont des volontaires, pas tous les développeurs."""
    st.info("Les répondants sont des volontaires ayant répondu à une enquête en ligne : "
            "les parts affichées décrivent ces répondants, pas l'ensemble des développeurs.",
            icon="ℹ️")
