"""Téléchargement et chargement des réponses à l'enquête. Fonctions pures, sans Streamlit."""
from __future__ import annotations

import shutil
import sys
import urllib.request
from pathlib import Path

import pandas as pd

from analysis import config


def _download(url: str, target: Path, min_bytes: int = 0) -> Path:
    """Télécharge url vers target en passant par un fichier temporaire.

    Le fichier final n'apparaît que si le téléchargement est complet : un téléchargement
    interrompu ne laisse jamais un CSV tronqué que l'application chargerait ensuite.
    """
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".part")
    print(f"Téléchargement de {url}", file=sys.stderr)
    request = urllib.request.Request(url, headers={"User-Agent": "dataviz-ece-project"})
    with urllib.request.urlopen(request, timeout=120) as response, open(tmp, "wb") as out:
        shutil.copyfileobj(response, out, length=1 << 20)
    size = tmp.stat().st_size
    if size < min_bytes:
        head = tmp.read_text(encoding="utf-8", errors="replace")[:200]
        tmp.unlink()
        raise RuntimeError(
            f"Fichier reçu trop petit ({size} octets) depuis {url}. "
            f"S'agit-il d'un pointeur Git LFS ? Début du contenu : {head!r}"
        )
    tmp.replace(target)
    print(f"Enregistré : {target} ({size / 1e6:.1f} Mo)", file=sys.stderr)
    return target


def ensure_data(year: int = config.MAIN_YEAR) -> Path:
    """Renvoie le chemin du fichier de réponses de l'année, en le téléchargeant s'il manque.

    Appelée au démarrage de l'application : un clone frais ou un déploiement sans données
    se remet en état tout seul.
    """
    target = config.results_path(year)
    if not target.exists():
        _download(config.SOURCES[year]["results"], target, config.MIN_RESULTS_BYTES)
    schema = config.schema_path(year)
    if not schema.exists():
        _download(config.SOURCES[year]["schema"], schema)
    return target


def load_survey(year: int = config.MAIN_YEAR, path: Path | None = None) -> pd.DataFrame:
    """Renvoie les réponses de l'année : une ligne par répondant, toutes les colonnes,
    plus une colonne `year`.

    Les colonnes numériques utiles (WorkExp, YearsCode, ConvertedCompYearly) sont converties
    en nombres ; une réponse non numérique devient manquante.
    """
    path = path or ensure_data(year)
    df = pd.read_csv(path, low_memory=False, encoding="utf-8-sig")
    for col in ("WorkExp", "YearsCode", "ConvertedCompYearly"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.assign(year=year)


def load_schema(year: int = config.MAIN_YEAR) -> pd.DataFrame:
    """Renvoie le dictionnaire des questions de l'année (colonne, question, type, effectif)."""
    ensure_data(year)
    return pd.read_csv(config.schema_path(year), encoding="utf-8-sig")


def question_text(schema: pd.DataFrame, column: str) -> str:
    """Renvoie l'intitulé anglais de la question derrière une colonne, ou le nom de la colonne."""
    # 2026 nomme la colonne « column », 2025 « qname ».
    key = "column" if "column" in schema.columns else "qname"
    match = schema.loc[schema[key] == column, "question"]
    return str(match.iloc[0]) if not match.empty else column
