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

- *Chaque responsable d'axe ajoute ici ses choix (question, filtres, figures, seuils).*

### Axe 1 · Adoption : où en sont les développeurs ? (Baptiste)

- **Question** : qui utilise l'IA au travail, quels types d'outils, à quelle fréquence, qui se
  forme ? Colonnes : `AISelect`, `AIFreq_1` à `AIFreq_4`, `AIDaily`, `LearnAI`, `LearnAIHow` ;
  segments `Age`, `WorkExp`, `Role`, `Employment`.
- **Comparaison** : France face aux 8 pays européens de la page principale (mêmes pays, mêmes
  couleurs : France en bleu, Europe en gris), pour que les axes se lisent comme la page principale.
- **Bases de calcul** : le questionnaire est filtré. `AIFreq_k` n'est posée qu'à ceux qui ont
  coché l'outil k dans `AISelect` (correspondance vérifiée sur les données : 100 % des répondants
  à `AIFreq_k` ont coché l'outil k), `AIDaily` qu'à ceux qui utilisent un outil chaque jour,
  `LearnAIHow` qu'à ceux qui se sont formés. Chaque indicateur est donc une colonne 0/1, vide
  hors de sa base, et chaque part est calculée sur sa propre base, affichée sous la figure.
- **Non-utilisateurs** : « I don't use AI tools » coché = non-utilisateur ; sans réponse à
  `AISelect` = hors base (on ne suppose pas qu'il n'utilise pas l'IA).
- **Segments** : expérience en 4 tranches (0-4, 5-9, 10-19, 20 ans et plus) ; les 41 postes de
  `Role` regroupés en 5 familles pour garder des groupes assez nombreux.
- **Seuil** : 100 répondants par zone, comme la page principale. Sous ce seuil, une figure ou
  un groupe n'est pas tracé et la page le dit. Marge d'erreur affichée : intervalle de confiance
  à 95 % (1,96 × √(p(1 − p)/n)) ; pour un écart, la marge combine les deux zones.
- **Méthode du cours** : la page suit les cinq temps de l'enquête. Le brief (conclusion d'abord,
  trois figures-affirmations, ce que nous savons / ne savons pas / recommandons) est dans
  « Le constat » ; « Mise à l'épreuve » contient la table de preuves (marge d'erreur, pays par
  pays, segments contre le paradoxe de Simpson, composition des répondants) et l'échelle des
  affirmations ; « Données et méthode » contient la biographie des données, qui répond à quoi et
  le journal « je remarque / je me demande ».
- **Titres affirmatifs** : comme sur la page principale, ils ne sont affichés que pour la
  population par défaut, où ils ont été vérifiés ; avec d'autres filtres, ils deviennent
  descriptifs. Les commentaires « Et alors ? » sont recalculés selon les filtres.
- **Résultat (population par défaut)** : 75 % des répondants français utilisent l'IA au
  travail contre 82 % en Europe (−6,8 points, ± 3,5) ; la France est sous chacun des 8 pays,
  l'écart tient à chaque niveau d'expérience et à composition égale (âge, expérience, poste).
  Chez les utilisateurs, l'usage quotidien est le même (72 %). La formation à l'IA au travail
  est plus rare (52 % contre 59 %).
- **Graphiques** : haltères Altair pour comparer France et Europe sur plusieurs indicateurs ;
  barres empilées pour les répartitions complètes, avec une légende écrite à la main (la légende
  Altair écrase les barres empilées dans Streamlit).

