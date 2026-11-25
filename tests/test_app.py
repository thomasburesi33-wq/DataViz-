"""Tests de fumée de l'interface avec le vrai jeu de données.

Ignorés si les données n'ont pas été téléchargées (uv run python get_data.py).
"""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from analysis import config

pytestmark = pytest.mark.skipif(
    not config.results_path(config.MAIN_YEAR).exists(),
    reason="données absentes : lancer uv run python get_data.py",
)

ROOT = Path(__file__).resolve().parent.parent
PAGES = [str(ROOT / "app.py")] + sorted(str(p) for p in (ROOT / "pages").glob("*.py"))


@pytest.mark.parametrize("page", PAGES, ids=lambda p: Path(p).name)
def test_page_runs_without_exception(page):
    at = AppTest.from_file(page, default_timeout=120).run()
    assert not at.exception, at.exception
    # Chaque page affiche au moins une phrase de population.
    assert any("Population :" in c.value for c in at.caption)
