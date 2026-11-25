# Harmonisation des réponses 2025 → 2026

Toute comparaison entre 2025 et 2026 s'appuie sur ce document et sur
`analysis/harmonisation.py`, qui l'applique. Une colonne absente de ce tableau **n'est pas
comparable** tant qu'une ligne n'y a pas été ajoutée, vérification faite.

Méthode : pour chaque paire, on compare l'intitulé de la question (`schema.csv` 2025 /
`survey_results_schema.csv` 2026) et l'ensemble des modalités observées dans les deux fichiers.

## Colonnes harmonisées

| 2025 | 2026 | Question | Modalités | Traitement |
| --- | --- | --- | --- | --- |
| `Country` | `Country` | Pays de résidence | Mêmes libellés ; quelques petits pays présents une seule année | Aucun (le filtre porte sur des pays présents les deux années) |
| `Age` | `Age` | Tranche d'âge | 2026 ajoute « Under 18 years old » | Modalité exclue des comparaisons (`EXCLUDE_VALUES`) |
| `Employment` | `Employment` | Situation professionnelle | 6 modalités identiques | Aucun |
| `OrgSize` | `OrgSize` | Taille de l'employeur | 9 modalités identiques | Aucun |
| `RemoteWork` | `WorkSetting` | Mode de travail (télétravail, hybride, sur site) | 5 modalités identiques | Renommage |
| `JobSat` | `JobSat` | Satisfaction au travail | 11 modalités identiques | Aucun |
| `WorkExp` | `WorkExp` | Années d'expérience professionnelle | Numérique | Conversion en nombre |
| `ConvertedCompYearly` | `ConvertedCompYearly` | Rémunération annuelle convertie en dollars | Numérique | Conversion en nombre ; taux de change propres à chaque année |
| `LanguageHaveWorkedWith` | `LanguagesHaveWorkedWith` | Langages utilisés (choix multiples) | 2026 ajoute Clojure, Haskell, Julia, Nix, Objective-C, Solidity | Renommage ; ne comparer que les langages proposés les deux années |

## Colonnes à ne pas comparer

| Colonne | Raison |
| --- | --- |
| `AISelect` | Même nom, autre question : choix unique sur la fréquence d'usage de l'IA en 2025, choix multiples sur les types d'outils en 2026 |
| `ICorPM` | 2 modalités en 2025, 4 en 2026 (nouvelles catégories mixtes) : pas de correspondance univoque |
| `MainBranch` (2025) / `CodeMain` (2026) | Questions différentes sur le rapport au code : le filtre « Rapport au code » n'est pas appliqué aux comparaisons |

## Population comparée

Mêmes filtres les deux années (pays, situation professionnelle). Les effectifs diffèrent
(49 191 répondants en 2025, 30 903 en 2026 ; 1 409 et 794 en France) : on compare des **parts**,
jamais des effectifs, et chaque figure affiche le n de chaque année.

## Journal

| Date | Auteur | Ajout |
| --- | --- | --- |
| 25/11/2026 | Baptiste | Première version : colonnes ci-dessus, vérifiées sur les fichiers des deux années |
