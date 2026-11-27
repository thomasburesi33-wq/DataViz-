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

Message : une politique d'usage de l'IA doit traiter les freins avant l'outillage. Parmi les répondants, ceux qui vivent en France utilisent moins l'IA, citent plus souvent l'environnement comme frein et ont plus de réserves que leurs voisins européens, mais font autant confiance à l'IA quand ils l'utilisent.
Indicateurs (4) : n'utilisent pas l'IA (AISelect), environnement comme frein et aucune réserve (AIAvoid), confiance si le résultat est vérifiable (AITrust). Chacun est affiché pour la France avec son écart en points avec l'Europe : c'est cet écart qui porte le message.
Figure-clé : haltères France / Europe. La France est en couleur (le message), l'Europe en gris (le contexte). Une seule figure-clé : les autres preuves sont le rôle des axes.
Onglets : « Le constat » (indicateurs et figure-clé, ouvert par défaut), « Explorer » (un indicateur pays par pays, graphique natif) et « Données » (la table derrière la figure).
Effectif minimal : 100 répondants par indicateur et par zone. La marge d'erreur d'une part calculée sur n répondants vaut au plus environ 1/√n, soit ±10 points pour n = 100. Les écarts France / Europe de la population par défaut sont de 7 à 15 points, calculés sur 490 à 650 répondants en France (marge ±4 à ±4,5 points). Sous 100 répondants, la page avertit et n'affiche pas de figure (st.warning puis st.stop) ; dans « Explorer », les pays sous ce seuil sont masqués et nommés.
Titre de la figure : il n'affirme le constat que pour la population par défaut (8 pays, tous âges), où il a été vérifié. Avec d'autres filtres, il devient descriptif.

## Axes


## Axe 4 · Usages, impact et organisation

- **Question** : pour quelles tâches l'IA est-elle jugée utile, à quel prix en erreurs, et
  comment les entreprises comparables encadrent-elles son usage ?
- **Population** : France face aux 8 pays européens de l'accueil (`analysis/accueil.py`),
  même seuil de 100 répondants (marge d'erreur ≤ ±10 points).
- **« Utile »** = « Useful » ou « Very useful » à `AIImpact_1…7`. Par défaut, la base compte
  tous les répondants à la question, « Not applicable » compris : une tâche que l'IA ne touche
  pas n'est pas une tâche où elle aide. Un interrupteur permet de l'exclure (la conception passe
  alors d'environ 40 % à 54 %, la communication de 27 % à 39 %).
- **Satisfaction** : « améliorée » = Somewhat ou Greatly improved, « dégradée » = Somewhat ou
  Greatly decreased (`AISat_1…7`), même tâche que `AIImpact_k`.
- **Taille d'entreprise** : deux groupes, 1 000 salariés et plus / moins de 1 000 ; les
  indépendants sont écartés (pas d'organisation à encadrer). Pas de filtre de taille : la
  comparaison par taille est faite dans la vue « Politique selon la taille », seule à
  l'exploiter dans le brief.
- **Figure-clé** : barres par tâche, France en couleur, Europe en gris (matplotlib, comme le
  recommande le cours). Le titre n'affirme le constat que sur la vue par défaut.
- **Onglets** : « Le constat » (4 indicateurs + figure-clé), « Explorer » (satisfaction par
  tâche, erreurs coûteuses, politique selon la taille), « Données » (toutes les tables).
- **Limites** : perceptions déclarées par des volontaires, pas des gains mesurés ; aucune
  cause démontrée ; secteur industriel non isolable.
