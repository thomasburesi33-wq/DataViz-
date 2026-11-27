"""Page principale : le sujet de l'analyse et sa source."""
import streamlit as st

st.set_page_config(page_title="IA et développeurs · DSI", layout="wide")

# --- Sujet de l'analyse ---
st.title("Quelle politique d'usage de l'IA pour nos développeurs ?")

st.markdown(
    """
**Commanditaire :** la DSI d'un grand groupe industriel français, présent en Europe
et engagé dans une démarche RSE.

**Sa question :** quels outils d'IA autoriser ou fournir à ses développeurs, pour quelles
tâches, avec quel accompagnement, et comment concilier cela avec ses engagements RSE ?

**Notre analyse :** comparer les répondants vivant en France à ceux de pays européens
voisins : usage de l'IA, freins, confiance, outils, impact sur le travail et politiques
des entreprises.
"""
)

# --- Source des données ---
st.subheader("Source")
st.markdown(
    """
- **Enquête Stack Overflow 2026** : [restitution officielle](https://survey.stackoverflow.co/2026)
- Données brutes : archive officielle
  [StackExchange/Survey](https://github.com/StackExchange/Survey), dossier `packages/archive/2026`
  (`survey_results_public.csv` et `survey_results_schema.csv`)
- 30 903 répondants dans le monde, dont 794 en France
"""
)
