"""Télécharge dans data/ les réponses à l'enquête Stack Overflow.

À lancer une fois après le clone :
    uv run python get_data.py              # 2026 seulement (~120 Mo)
    uv run python get_data.py --with-2025  # ajoute 2025 pour les comparaisons (~140 Mo)

Les fichiers déjà présents ne sont pas retéléchargés. L'application télécharge aussi
les données d'elle-même au premier lancement si elles manquent.
"""
import argparse

from analysis import config, load


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--with-2025", action="store_true",
                        help="télécharge aussi l'enquête 2025 (comparaisons)")
    args = parser.parse_args()

    years = [config.MAIN_YEAR] + ([config.COMPARISON_YEAR] if args.with_2025 else [])
    for year in years:
        path = load.ensure_data(year)
        print(f"{year} prêt : {path} ({path.stat().st_size / 1e6:.1f} Mo)")


if __name__ == "__main__":
    main()
