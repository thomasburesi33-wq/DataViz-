"""Données synthétiques : les tests tournent sans télécharger l'enquête."""
import pandas as pd
import pytest


@pytest.fixture
def survey() -> pd.DataFrame:
    return pd.DataFrame({
        "ResponseId": [1, 2, 3, 4, 5, 6],
        "Country": ["France", "France", "France", "Germany", "France", None],
        "CodeMain": ["I create code as a primary part of my job",
                     "I create code occasionally",
                     "I create code as a primary part of my job",
                     "I create code as a primary part of my job",
                     None,
                     "I do not create code"],
        "Employment": ["Employed", "Student", "Employed", "Employed", "Employed", None],
        "WorkSetting": ["Remote", "Remote", "In-person", "Remote", None, None],
        "OrgSize": ["20 to 99 employees"] * 3 + ["Less than 20 employees"] * 3,
        "Age": ["25-34 years old", "18-24 years old", "25-34 years old",
                "35-44 years old", "Under 18 years old", "25-34 years old"],
        "LanguagesHaveWorkedWith": ["Python;SQL", "Python", None, "Rust;Python", "SQL", None],
        "WorkExp": [3, None, 10, 5, 1, None],
        "ConvertedCompYearly": [50000, None, 70000, 80000, None, None],
        "year": 2026,
    })
