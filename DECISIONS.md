# Décisions de conception

Chaque choix est consigné **au moment où il est fait**, avec sa raison. Ajoutez une ligne datée
et signée plutôt que de réécrire une décision passée.

## Population

- **Population par défaut : répondants résidant en France** (`Country == "France"`, 794 répondants
  en 2026). Raison : le commanditaire est sur le marché français. Le filtre « Pays » permet d'élargir
  à d'autres pays pour comparer.
- Les répondants sont des volontaires d'une enquête en ligne : chaque page le rappelle, aucune part
  n'est présentée comme celle de tous les développeurs.
- Une question à choix multiples a pour base les répondants **ayant répondu à cette question**,
  pas toute la population : la phrase de population sous la figure donne cette base.

## Effectif minimal

- **Seuil : 30 répondants** (`config.MIN_N`). Sous ce seuil, une médiane n'est pas tracée et la
  page affiche un avertissement. Raison : à faible effectif, une part ou une médiane varie trop
  d'un échantillon à l'autre pour être interprétée. À réévaluer par chaque axe si besoin.

## Données et reproductibilité

- Environnement géré par **uv** (`pyproject.toml` + `uv.lock`), Python 3.12, versions épinglées :
  le même environnement sur macOS, Linux et Windows.
- Données téléchargées depuis `media.githubusercontent.com` (et non le lien « raw », qui renvoie un
  pointeur Git LFS). Téléchargement atomique et contrôle de taille.
- L'application télécharge les données si elles manquent : un clone frais ou un déploiement
  fonctionne sans étape manuelle.
- Une intégration continue (GitHub Actions) vérifie l'installation et les tests sur les trois
  systèmes à chaque push.
- `uv.lock` est généré par GitHub Actions (`.github/workflows/lock.yml`) à chaque modification de
  `pyproject.toml` sur `main`, s'il n'a pas été commité avec : le verrou ne peut pas diverger des
  dépendances déclarées.

## Cache et session

- Cache sur le chargement uniquement (voir `ARCHITECTURE.md`).
- Filtres de population communs à toutes les pages, conservés en session.

## Graphiques

- Barres horizontales pour les parts : les libellés des modalités, souvent longs, restent lisibles.
- Une seule teinte (`#257de0`) quand la figure n'a qu'une série ; deuxième teinte (`#f47230`)
  réservée à une seconde série (par exemple 2025 face à 2026).
- Valeur affichée au bout de chaque barre, grille discrète, pas d'axe secondaire.

## Tableau de bord principal

- *À compléter : message retenu, figure-clé, indicateurs du bandeau, et pourquoi.*

## Axes

- *Chaque responsable d'axe ajoute ici ses choix (question, filtres, figures, seuils).*
